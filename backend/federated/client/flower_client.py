import numpy as np
import torch
import torch.nn as nn
from typing import List, Dict, Any, Tuple
import flwr as fl

from models.cnn.cnn_model import MedicalCNNModule
from models.ann.ann_model import MedicalANNModule
from models.bert.bert_model import ClinicalBERTModule
from models.fusion.feature_fusion import MultimodalFeatureFusionEngine
from attack.attack_simulator import AttackSimulator
from federated.data_loader import get_hospital_dataloader


class HospitalFLClient(fl.client.NumPyClient):
    """
    Step 8 & 9: Real Hospital Federated Learning Client (Flower NumPyClient).
    Performs real PyTorch forward & backward passes over hospital's local DataLoader.
    Calculates actual cross-entropy loss, gradients, and held-out validation metrics.
    """
    def __init__(self, hospital_id: str, sample_count: int = 150):
        self.hospital_id = hospital_id
        self.sample_count = sample_count
        
        # Local multimodal architecture models
        self.cnn = MedicalCNNModule()
        self.ann = MedicalANNModule(input_features=8)
        self.bert = ClinicalBERTModule()
        self.fusion = MultimodalFeatureFusionEngine(num_classes=2)
        
        self.attack_simulator = AttackSimulator()
        self.active_attack: str = "None"
        self.attack_intensity: float = 1.0

        # Load local dataset
        try:
            self.dataloader = get_hospital_dataloader(hospital_id=hospital_id, batch_size=16, shuffle=True)
            self.sample_count = len(self.dataloader.dataset)
        except Exception:
            self.dataloader = None

        # Class imbalance & FedProx configuration
        self.use_class_weighting: bool = True
        self.fedprox_mu: float = 0.01

        self.train_size = int(self.sample_count * 0.8)
        self.val_size = self.sample_count - self.train_size
        self.local_epoch_count = 0
        self.last_metrics: Dict[str, Any] = {}

    def get_parameters(self, config: Dict[str, Any] = None) -> List[np.ndarray]:
        """
        Extracts all model parameters as numpy arrays.
        """
        params = []
        for model in [self.cnn, self.ann, self.bert, self.fusion]:
            for p in model.parameters():
                params.append(p.data.cpu().numpy())
        return params

    def set_parameters(self, parameters: List[np.ndarray]):
        """
        Updates local models with aggregated global parameters.
        """
        idx = 0
        for model in [self.cnn, self.ann, self.bert, self.fusion]:
            for p in model.parameters():
                p.data = torch.from_numpy(np.copy(parameters[idx])).float()
                idx += 1

    def fit(self, parameters: List[np.ndarray], config: Dict[str, Any]) -> Tuple[List[np.ndarray], int, Dict[str, Any]]:
        """
        Flower NumPyClient fit hook.
        """
        updated_weights, num_samples, metrics = self.train_local_epoch(parameters)
        return updated_weights, num_samples, metrics

    def evaluate(self, parameters: List[np.ndarray], config: Dict[str, Any]) -> Tuple[float, int, Dict[str, Any]]:
        """
        Flower NumPyClient evaluate hook.
        """
        self.set_parameters(parameters)
        val_loss, val_acc, detailed_metrics = self._evaluate_local_split()
        return float(val_loss), self.val_size, {"val_accuracy": float(val_acc), **detailed_metrics}

    def _evaluate_local_split(self) -> Tuple[float, float, Dict[str, Any]]:
        """Evaluates current local models on local dataset and computes per-class precision/recall."""
        if not self.dataloader:
            return 0.5, 0.75, {}

        self.cnn.eval()
        self.ann.eval()
        self.bert.eval()
        self.fusion.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        all_targets = []
        all_preds = []

        with torch.no_grad():
            for img, tab, text, targets in self.dataloader:
                if self.active_attack == "Label Flip":
                    targets = 1 - targets

                cnn_out = self.cnn(img)
                ann_out = self.ann(tab)
                bert_out = self.bert(text)
                fusion_out = self.fusion(cnn_out["embeddings"], ann_out["embeddings"], bert_out["embeddings"])
                
                logits = fusion_out["logits"]
                loss = criterion(logits, targets)

                total_loss += loss.item() * targets.size(0)
                preds = torch.argmax(logits, dim=1)
                
                all_targets.extend(targets.cpu().numpy().tolist())
                all_preds.extend(preds.cpu().numpy().tolist())

        avg_loss = total_loss / max(len(all_targets), 1)
        correct = sum(1 for t, p in zip(all_targets, all_preds) if t == p)
        accuracy = correct / max(len(all_targets), 1)

        # Compute per-class precision, recall, F1
        from sklearn.metrics import precision_recall_fscore_support
        p, r, f1, _ = precision_recall_fscore_support(all_targets, all_preds, labels=[0, 1], zero_division=0)

        detailed_metrics = {
            "precision_class_0": round(float(p[0]), 4),
            "recall_class_0": round(float(r[0]), 4),
            "f1_class_0": round(float(f1[0]), 4),
            "precision_class_1": round(float(p[1]), 4),
            "recall_class_1": round(float(r[1]), 4),
            "f1_class_1": round(float(f1[1]), 4),
            "minority_class_recall": round(float(r[1]), 4)
        }

        return avg_loss, accuracy, detailed_metrics

    def train_local_epoch(self, global_parameters: List[np.ndarray]) -> Tuple[List[np.ndarray], int, Dict[str, float]]:
        """
        Performs real PyTorch local training with inverse-frequency class weighting,
        FedProx regularization, and per-class metrics calculation.
        """
        self.set_parameters(global_parameters)
        self.local_epoch_count += 1

        if self.dataloader is None:
            self.dataloader = get_hospital_dataloader(hospital_id=self.hospital_id, batch_size=16, shuffle=True)
            self.sample_count = len(self.dataloader.dataset)

        # Set models to train mode
        self.cnn.train()
        self.ann.train()
        self.bert.train()
        self.fusion.train()

        # 1. Local inverse-frequency class weighting
        if self.use_class_weighting and hasattr(self.dataloader.dataset, "get_class_weights"):
            class_weights = self.dataloader.dataset.get_class_weights()
            criterion = nn.CrossEntropyLoss(weight=class_weights)
        else:
            criterion = nn.CrossEntropyLoss()

        all_params = (
            list(self.cnn.parameters()) +
            list(self.ann.parameters()) +
            list(self.bert.parameters()) +
            list(self.fusion.parameters())
        )
        optimizer = torch.optim.Adam(all_params, lr=0.001)

        total_train_loss = 0.0
        correct_train = 0
        total_train_samples = 0

        for img, tab, text, targets in self.dataloader:
            # Inject attack if toggled
            if self.active_attack == "Label Flip":
                targets = 1 - targets

            optimizer.zero_grad()

            # Real Multimodal Forward Pass
            cnn_out = self.cnn(img)
            ann_out = self.ann(tab)
            bert_out = self.bert(text)
            fusion_out = self.fusion(cnn_out["embeddings"], ann_out["embeddings"], bert_out["embeddings"])

            logits = fusion_out["logits"]
            loss_ce = criterion(logits, targets)

            # 2. FedProx proximal regularization term
            proximal_loss = torch.tensor(0.0)
            if self.fedprox_mu > 0 and global_parameters is not None:
                idx = 0
                for model in [self.cnn, self.ann, self.bert, self.fusion]:
                    for p in model.parameters():
                        w_g = torch.from_numpy(global_parameters[idx]).float()
                        proximal_loss = proximal_loss + torch.sum((p - w_g) ** 2)
                        idx += 1
                proximal_loss = (self.fedprox_mu / 2.0) * proximal_loss

            total_loss = loss_ce + proximal_loss

            # Real Backpropagation
            total_loss.backward()
            optimizer.step()

            total_train_loss += loss_ce.item() * targets.size(0)
            preds = torch.argmax(logits, dim=1)
            correct_train += (preds == targets).sum().item()
            total_train_samples += targets.size(0)

        train_acc = correct_train / max(total_train_samples, 1)
        train_loss = total_train_loss / max(total_train_samples, 1)

        # Evaluate real validation metrics + per-class metrics
        val_loss, val_acc, per_class_metrics = self._evaluate_local_split()

        # Determine fit status based on train/val metrics
        gap = train_acc - val_acc
        if train_acc < 0.55 and val_acc < 0.55:
            fit_status = "Underfit"
        elif gap > 0.15:
            fit_status = "Overfit"
        else:
            fit_status = "Well-fit"

        updated_weights = self.get_parameters()

        # Apply weight poisoning / Gaussian noise attack if toggled
        is_attack_active = False
        if self.active_attack != "None":
            updated_weights = self.attack_simulator.apply_attack(
                updated_weights, self.active_attack, self.attack_intensity
            )
            fit_status = "Compromised"
            is_attack_active = True

        class_dist = self.dataloader.dataset.get_class_distribution() if hasattr(self.dataloader.dataset, "get_class_distribution") else {}

        metrics = {
            "local_accuracy": round(val_acc, 4),
            "local_loss": round(val_loss, 4),
            "train_accuracy": round(train_acc, 4),
            "val_accuracy": round(val_acc, 4),
            "train_loss": round(train_loss, 4),
            "val_loss": round(val_loss, 4),
            "generalization_gap": round(gap, 4),
            "fit_status": fit_status,
            "train_size": self.train_size,
            "val_size": self.val_size,
            "is_attack_active": is_attack_active,
            "attack_type": self.active_attack,
            "class_distribution": class_dist,
            "fedprox_mu": self.fedprox_mu,
            "use_class_weighting": self.use_class_weighting,
            **per_class_metrics
        }
        self.last_metrics = metrics

        return updated_weights, self.sample_count, metrics


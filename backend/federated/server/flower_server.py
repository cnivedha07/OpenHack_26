import numpy as np
import torch
import torch.nn as nn
from typing import Dict, List, Any, Tuple, Optional
import flwr as fl
from flwr.server.strategy import FedAvg
from flwr.server.client_proxy import ClientProxy
from flwr.common import FitRes, Parameters, Scalar, ndarrays_to_parameters, parameters_to_ndarrays


from federated.client.flower_client import HospitalFLClient
from trust.trust_engine import TrustEngine
from aggregation.trust_aggregator import TrustWeightedAggregator
from models.cnn.cnn_model import MedicalCNNModule
from models.ann.ann_model import MedicalANNModule
from models.bert.bert_model import ClinicalBERTModule
from models.fusion.feature_fusion import MultimodalFeatureFusionEngine
from federated.data_loader import get_hospital_dataloader


class TrustWeightedFlowerStrategy(FedAvg):
    """
    Step 9: Custom Flower Strategy Subclass.
    Integrates TrustEngine Z-Score filtering and TrustWeightedAggregator into Flower's aggregate_fit lifecycle.
    """
    def __init__(self, trust_engine: TrustEngine, aggregator: TrustWeightedAggregator, server_manager: 'FederatedServerManager', **kwargs):
        super().__init__(**kwargs)
        self.trust_engine = trust_engine
        self.aggregator = aggregator
        self.server_manager = server_manager

    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[BaseException]
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        if not results:
            return None, {}

        hospital_round_updates = {}
        client_payloads = []

        for client_proxy, fit_res in results:
            hid = getattr(client_proxy, "cid", f"hospital_{len(client_payloads)+1}")
            weights = parameters_to_ndarrays(fit_res.parameters)
            sample_cnt = fit_res.num_examples
            metrics = fit_res.metrics or {}

            # Calculate client update metrics relative to global parameters
            stat_metrics = self.trust_engine.compute_client_metrics(weights, self.server_manager.global_weights)
            stat_metrics["local_accuracy"] = metrics.get("val_accuracy", 0.75)
            stat_metrics["local_loss"] = metrics.get("val_loss", 0.5)

            hospital_round_updates[hid] = {
                "weights": weights,
                "sample_count": sample_cnt,
                "metrics": stat_metrics,
                "is_attack_active": metrics.get("is_attack_active", False),
                "attack_type": metrics.get("attack_type", "None")
            }

        # Evaluate Trust Scores
        trust_eval, updated_trust_scores = self.trust_engine.evaluate_round_trust(
            hospital_round_updates, self.server_manager.trust_scores
        )
        self.server_manager.trust_scores = updated_trust_scores

        for hid, update_info in hospital_round_updates.items():
            trust_val = self.server_manager.trust_scores.get(hid, 100.0)
            client_payloads.append((
                update_info["weights"],
                update_info["sample_count"],
                trust_val,
                hid
            ))

        new_weights = self.aggregator.aggregate_weights(client_payloads, min_trust_threshold=40.0)
        return ndarrays_to_parameters(new_weights), {"participating_count": len(client_payloads)}



class FederatedServerManager:
    """
    Step 9, 10, 11: Real Federated Learning Server Manager.
    Orchestrates Flower FL training, PyTorch global model evaluation, and trust aggregation.
    """
    def __init__(self):
        self.current_round = 0
        self.total_rounds = 10
        self.is_training_active = False
        self.is_paused = False

        # Differential Privacy parameters
        self.dp_enabled = False
        self.dp_clip_norm = 3.0
        self.dp_noise_sigma = 0.15

        # Global multimodal architecture models
        self.global_cnn = MedicalCNNModule()
        self.global_ann = MedicalANNModule(input_features=8)
        self.global_bert = ClinicalBERTModule()
        self.global_fusion = MultimodalFeatureFusionEngine(num_classes=2)

        # Initialize global parameters
        self.global_weights = self._extract_global_parameters()

        # Hospital client nodes
        self.clients: Dict[str, HospitalFLClient] = {
            "hospital_1": HospitalFLClient("hospital_1", sample_count=180),
            "hospital_2": HospitalFLClient("hospital_2", sample_count=220),
            "hospital_3": HospitalFLClient("hospital_3", sample_count=140),
            "hospital_4": HospitalFLClient("hospital_4", sample_count=200)
        }

        # Dynamic Trust Scores (Start = 100.0)
        self.trust_scores: Dict[str, float] = {
            "hospital_1": 100.0,
            "hospital_2": 100.0,
            "hospital_3": 100.0,
            "hospital_4": 100.0
        }

        self.trust_engine = TrustEngine()
        self.aggregator = TrustWeightedAggregator()
        self.flower_strategy = TrustWeightedFlowerStrategy(
            trust_engine=self.trust_engine,
            aggregator=self.aggregator,
            server_manager=self
        )

        # Global accuracy & loss metrics
        self.global_accuracy = 0.75
        self.global_loss = 0.55
        self.round_history: List[Dict[str, Any]] = []
        self.last_round_client_metrics: Dict[str, Any] = {}
        self.modality_weights: Dict[str, float] = {
            "CNN (Vision)": 38.5,
            "ANN (Tabular)": 31.2,
            "BERT (Text)": 30.3
        }

    def _extract_global_parameters(self) -> List[np.ndarray]:
        params = []
        for model in [self.global_cnn, self.global_ann, self.global_bert, self.global_fusion]:
            for p in model.parameters():
                params.append(p.data.cpu().numpy())
        return params

    def set_global_parameters(self, parameters: List[np.ndarray]):
        idx = 0
        for model in [self.global_cnn, self.global_ann, self.global_bert, self.global_fusion]:
            for p in model.parameters():
                p.data = torch.from_numpy(parameters[idx]).float()
                idx += 1
        self.global_weights = parameters

    def _apply_differential_privacy(self, weights: List[np.ndarray]) -> List[np.ndarray]:
        flat = np.concatenate([w.flatten() for w in weights])
        norm = np.linalg.norm(flat) + 1e-8
        clip_factor = min(1.0, self.dp_clip_norm / norm)

        noisy_weights = []
        for w in weights:
            clipped = w * clip_factor
            noise = np.random.normal(loc=0.0, scale=self.dp_noise_sigma, size=w.shape)
            noisy_weights.append((clipped + noise).astype(np.float32))
        return noisy_weights

    def toggle_differential_privacy(self, enabled: bool):
        self.dp_enabled = enabled
        return {"dp_enabled": self.dp_enabled, "clip_norm": self.dp_clip_norm, "noise_sigma": self.dp_noise_sigma}

    def pause_training(self):
        self.is_paused = True
        self.is_training_active = False

    def resume_training(self):
        self.is_paused = False
        self.is_training_active = True

    def reset_training(self):
        self.current_round = 0
        self.is_training_active = False
        self.is_paused = False
        self.global_accuracy = 0.75
        self.global_loss = 0.55
        self.round_history = []
        self.last_round_client_metrics = {}
        for hid in self.trust_scores:
            self.trust_scores[hid] = 100.0
        for client in self.clients.values():
            client.local_epoch_count = 0
            client.active_attack = "None"
            client.last_metrics = {}
        self.global_weights = self._extract_global_parameters()

    def toggle_attack(self, hospital_id: str, attack_type: str, intensity: float = 1.0):
        if hospital_id in self.clients:
            self.clients[hospital_id].active_attack = attack_type
            self.clients[hospital_id].attack_intensity = intensity
            return True
        return False

    def _evaluate_global_model(self) -> Tuple[float, float, Dict[str, float]]:
        """
        Runs a real PyTorch forward pass of the global model over validation data.
        Returns (global_loss, global_accuracy, modality_weights).
        """
        self.global_cnn.eval()
        self.global_ann.eval()
        self.global_bert.eval()
        self.global_fusion.eval()

        criterion = nn.CrossEntropyLoss()
        total_loss = 0.0
        correct = 0
        total_samples = 0
        mod_weights_sum = {"cnn": 0.0, "ann": 0.0, "bert": 0.0}
        batch_count = 0

        # Evaluate across hospital dataloaders
        with torch.no_grad():
            for hid, client in self.clients.items():
                if not client.dataloader:
                    continue
                for img, tab, text, targets in client.dataloader:
                    cnn_out = self.global_cnn(img)
                    ann_out = self.global_ann(tab)
                    bert_out = self.global_bert(text)
                    fusion_out = self.global_fusion(cnn_out["embeddings"], ann_out["embeddings"], bert_out["embeddings"])

                    logits = fusion_out["logits"]
                    loss = criterion(logits, targets)

                    total_loss += loss.item() * targets.size(0)
                    preds = torch.argmax(logits, dim=1)
                    correct += (preds == targets).sum().item()
                    total_samples += targets.size(0)

                    mb = fusion_out["modality_breakdown"]
                    mod_weights_sum["cnn"] += mb["cnn_weight"]
                    mod_weights_sum["ann"] += mb["ann_weight"]
                    mod_weights_sum["bert"] += mb["bert_weight"]
                    batch_count += 1

        avg_loss = total_loss / max(total_samples, 1)
        accuracy = correct / max(total_samples, 1)

        if batch_count > 0:
            c = mod_weights_sum["cnn"] / batch_count
            a = mod_weights_sum["ann"] / batch_count
            b = mod_weights_sum["bert"] / batch_count
            s = c + a + b + 1e-8
            modality_dist = {
                "CNN (Vision)": round((c / s) * 100.0, 1),
                "ANN (Tabular)": round((a / s) * 100.0, 1),
                "BERT (Text)": round((b / s) * 100.0, 1)
            }
        else:
            modality_dist = self.modality_weights

        return float(avg_loss), float(accuracy), modality_dist

    def execute_next_round(self, db: Any = None) -> Dict[str, Any]:
        """
        Executes a single federated learning round using real PyTorch updates and persisting results.
        """
        from utils.logger import log_event
        from database.models import RoundLogModel, GlobalModelVersionModel

        self.current_round += 1
        hospital_round_updates = {}
        client_payloads_for_aggregation = []

        # 1. Local Training on each active hospital
        for hid, client in self.clients.items():
            current_trust = self.trust_scores.get(hid, 100.0)
            
            # Skip training if hospital is excluded (trust < 40)
            if current_trust < 40.0:
                log_event(f"[Round {self.current_round}] Hospital {hid} excluded from round (Trust score: {current_trust:.1f} < 40.0)", level="warning")
                continue

            # Real PyTorch training step
            client_weights, sample_cnt, client_metrics = client.train_local_epoch(self.global_weights)

            # Compute update metrics relative to global model
            stat_metrics = self.trust_engine.compute_client_metrics(client_weights, self.global_weights)
            stat_metrics["local_accuracy"] = client_metrics["local_accuracy"]
            stat_metrics["local_loss"] = client_metrics["local_loss"]

            hospital_round_updates[hid] = {
                "weights": client_weights,
                "sample_count": sample_cnt,
                "metrics": stat_metrics,
                "is_attack_active": client_metrics["is_attack_active"],
                "attack_type": client_metrics["attack_type"]
            }

        # 2. Evaluate Round Trust Scores & Z-Scores
        trust_eval, updated_trust_scores = self.trust_engine.evaluate_round_trust(
            hospital_round_updates, self.trust_scores
        )
        self.trust_scores = updated_trust_scores

        # 3. Aggregate Trusted Updates
        for hid, update_info in hospital_round_updates.items():
            trust_val = self.trust_scores.get(hid, 100.0)
            client_payloads_for_aggregation.append((
                update_info["weights"],
                update_info["sample_count"],
                trust_val,
                hid
            ))

        new_global_weights = self.aggregator.aggregate_weights(
            client_payloads_for_aggregation, min_trust_threshold=40.0
        )

        if self.dp_enabled:
            new_global_weights = self._apply_differential_privacy(new_global_weights)

        self.set_global_parameters(new_global_weights)

        # Track fit diagnostics per hospital for this round
        self.last_round_client_metrics = {
            hid: info["metrics"] for hid, info in hospital_round_updates.items()
        }

        # 4. Evaluate Global Model Performance over validation datasets
        real_loss, real_acc, mod_dist = self._evaluate_global_model()
        self.global_loss = round(real_loss, 4)
        self.global_accuracy = round(real_acc, 4)
        self.modality_weights = mod_dist

        participating_hospitals = [item[3] for item in client_payloads_for_aggregation]

        # 5. Persist Round Logs to Database
        close_db_after = False
        if db is None:
            try:
                from database.database import SessionLocal
                db = SessionLocal()
                close_db_after = True
            except Exception as e:
                log_event(f"Could not open DB session for round persistence: {e}", level="warning")

        if db:
            try:
                # Save per-hospital round logs
                for hid, eval_info in trust_eval.items():
                    round_log = RoundLogModel(
                        round_number=self.current_round,
                        hospital_id=hid,
                        trust_score_before=eval_info.get("trust_score_before", 100.0),
                        trust_score_after=eval_info.get("trust_score_after", 100.0),
                        z_score=eval_info.get("z_score", 0.0),
                        cosine_similarity=eval_info.get("cosine_similarity", 1.0),
                        euclidean_distance=eval_info.get("euclidean_distance", 0.0),
                        gradient_norm=eval_info.get("gradient_norm", 0.0),
                        local_loss=eval_info.get("local_loss", 0.5),
                        local_accuracy=eval_info.get("local_accuracy", 0.8),
                        is_suspicious=eval_info.get("is_suspicious", False),
                        status_note=eval_info.get("status_note", "Normal Execution")
                    )
                    db.add(round_log)

                # Save global model version entry
                global_version = GlobalModelVersionModel(
                    version=f"v2.{self.current_round}.0",
                    round_number=self.current_round,
                    global_accuracy=self.global_accuracy,
                    global_loss=self.global_loss,
                    participating_hospitals=participating_hospitals,
                    trust_weighted_agg=True
                )
                db.add(global_version)
                db.commit()
            except Exception as ex:
                db.rollback()
                log_event(f"Failed to persist round logs to DB: {ex}", level="error")
            finally:
                if close_db_after:
                    db.close()

        round_summary = {
            "round_number": self.current_round,
            "global_accuracy": self.global_accuracy,
            "global_loss": self.global_loss,
            "hospitals_eval": trust_eval,
            "active_trust_scores": self.trust_scores,
            "participating_count": len(client_payloads_for_aggregation)
        }

        self.round_history.append(round_summary)
        log_event(f"[Round {self.current_round}] Real FL PyTorch training complete. Global accuracy: {self.global_accuracy:.4f}, Loss: {self.global_loss:.4f}")
        return round_summary

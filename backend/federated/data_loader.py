import os
import torch
import numpy as np
import pandas as pd
from typing import Tuple, Dict, Any
from torch.utils.data import Dataset, DataLoader


class MultimodalHealthcareDataset(Dataset):
    """
    Step 8 & 9: PyTorch Multimodal Dataset for Healthcare FL.
    Loads Tabular Vitals, Tokenized Text Notes, Synthetic Medical Scan Tensors, and Target Risk Labels.
    """
    def __init__(self, csv_path: str, max_text_len: int = 32):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Dataset CSV not found at: {csv_path}")

        self.df = pd.read_csv(csv_path)
        self.max_text_len = max_text_len

        # Extract Tabular Features (8 continuous clinical features)
        self.tabular_cols = [
            "age", "blood_pressure", "heart_rate", "oxygen_saturation",
            "blood_sugar", "bmi", "hemoglobin", "platelets"
        ]
        
        tab_raw = self.df[self.tabular_cols].values.astype(np.float32)
        # Normalize tabular features
        self.tab_mean = np.mean(tab_raw, axis=0)
        self.tab_std = np.std(tab_raw, axis=0) + 1e-6
        self.tabular_data = (tab_raw - self.tab_mean) / self.tab_std

        # Extract Target Labels (risk_level: 0 or 1)
        if "risk_level" in self.df.columns:
            self.labels = self.df["risk_level"].values.astype(np.int64)
        else:
            # Fallback threshold labeling
            bp = self.df["blood_pressure"].values
            o2 = self.df["oxygen_saturation"].values
            self.labels = ((bp > 135) | (o2 < 95.0)).astype(np.int64)

        # Pre-generate tokenized representations for doctor_notes
        notes = self.df["doctor_notes"].fillna("").astype(str).tolist()
        self.text_tensors = [self._tokenize_text(note) for note in notes]

    def get_class_weights(self) -> torch.Tensor:
        """
        Computes inverse-frequency class weights vector [w0, w1] for weighted loss calculation.
        """
        classes, counts = np.unique(self.labels, return_counts=True)
        total_samples = len(self.labels)
        num_classes = 2
        
        weights = np.ones(num_classes, dtype=np.float32)
        for c, cnt in zip(classes, counts):
            if c < num_classes and cnt > 0:
                weights[c] = total_samples / (num_classes * cnt)
        return torch.tensor(weights, dtype=torch.float32)

    def get_class_distribution(self) -> Dict[str, float]:
        """
        Returns class distribution ratios (e.g., class_0_ratio, class_1_ratio).
        """
        total = len(self.labels)
        pos = int(np.sum(self.labels == 1))
        neg = total - pos
        return {
            "class_0_ratio": round(neg / max(total, 1), 4),
            "class_1_ratio": round(pos / max(total, 1), 4),
            "total_samples": total
        }

    def _tokenize_text(self, text: str) -> torch.Tensor:
        """Simple deterministic word-index tokenizer mapping clinical notes to fixed-length tensors."""
        words = text.lower().replace(".", "").replace(",", "").split()
        indices = [abs(hash(w)) % 4999 + 1 for w in words[:self.max_text_len]]
        if len(indices) < self.max_text_len:
            indices += [0] * (self.max_text_len - len(indices))
        return torch.tensor(indices, dtype=torch.long)



    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        # 1. Tabular features (8-dim)
        tab_tensor = torch.tensor(self.tabular_data[idx], dtype=torch.float32)

        # 2. Text tokens (max_text_len)
        text_tensor = self.text_tensors[idx]

        # 3. Synthetic Medical Image Scan (3, 64, 64) generated deterministically per patient ID
        p_id = self.df.iloc[idx]["patient_id"]
        seed = abs(hash(p_id)) % (2**32)
        rng = np.random.default_rng(seed)
        
        # Base anatomical scan structure (circular pattern + random noise)
        x = np.linspace(-1, 1, 64)
        y = np.linspace(-1, 1, 64)
        xx, yy = np.meshgrid(x, y)
        r = np.sqrt(xx**2 + yy**2)
        scan = np.exp(-r**2 * 4.0)
        
        # Add patient specific variation and 3 channels
        img_arr = np.zeros((3, 64, 64), dtype=np.float32)
        img_arr[0] = scan + rng.normal(0, 0.05, (64, 64))
        img_arr[1] = scan * 0.8 + rng.normal(0, 0.05, (64, 64))
        img_arr[2] = scan * 0.5 + rng.normal(0, 0.05, (64, 64))
        img_tensor = torch.tensor(np.clip(img_arr, 0.0, 1.0), dtype=torch.float32)

        # 4. Target label
        label_tensor = torch.tensor(self.labels[idx], dtype=torch.long)

        return img_tensor, tab_tensor, text_tensor, label_tensor


def get_hospital_dataloader(
    hospital_id: str,
    batch_size: int = 16,
    shuffle: bool = True,
    data_dir: str = None
) -> DataLoader:
    """
    Returns a PyTorch DataLoader for a specific hospital's local dataset.
    Preserves data locality — patient data never leaves this loader.
    """
    if data_dir is None:
        base_dir = os.path.dirname(os.path.dirname(__file__))
        data_dir = os.path.join(base_dir, "synthetic_data")

    csv_path = os.path.join(data_dir, hospital_id, "vitals_data.csv")
    dataset = MultimodalHealthcareDataset(csv_path=csv_path)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle)

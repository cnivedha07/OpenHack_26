import numpy as np
from typing import List, Dict, Any

class AttackSimulator:
    """
    Attack Simulation Engine
    Supports on-demand injection of malicious attacks for hackathon defense demonstration:
    - Random Noise Injection
    - Gradient Poisoning
    - Label Flipping
    - Model Poisoning
    - Backdoor Attack
    - Sybil Attack
    - Data Poisoning
    """

    def apply_attack(
        self,
        weights: List[np.ndarray],
        attack_type: str,
        intensity: float = 1.0
    ) -> List[np.ndarray]:
        poisoned_weights = []

        if attack_type == "Random Noise Injection":
            for w in weights:
                noise = np.random.normal(loc=0.0, scale=0.5 * intensity, size=w.shape)
                poisoned_weights.append(w + noise)

        elif attack_type == "Gradient Poisoning":
            for w in weights:
                # Invert parameter updates / scale negatively
                poisoned_weights.append(-1.5 * w * intensity)

        elif attack_type == "Label Flipping":
            for w in weights:
                # Target final classification layer corruption
                poisoned_weights.append(w * -0.8 + np.random.uniform(-0.2, 0.2, size=w.shape))

        elif attack_type == "Model Poisoning":
            for w in weights:
                # Explode weights by extreme factor
                poisoned_weights.append(w * 10.0 * intensity)

        elif attack_type == "Backdoor Attack":
            for i, w in enumerate(weights):
                p_w = w.copy()
                if i == 0: # Modify first layer feature extractor
                    p_w[:2, :2] += 5.0 * intensity
                poisoned_weights.append(p_w)

        elif attack_type == "Sybil Attack":
            for w in weights:
                poisoned_weights.append(w + np.random.laplace(0.0, 0.8 * intensity, size=w.shape))

        elif attack_type == "Data Poisoning":
            for w in weights:
                poisoned_weights.append(w + np.random.standard_t(df=2, size=w.shape) * 0.4)

        else: # No attack
            poisoned_weights = [w.copy() for w in weights]

        return poisoned_weights

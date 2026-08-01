import numpy as np
from typing import List, Dict, Any, Tuple

class TrustWeightedAggregator:
    """
    Step 10 & 11: Trust-Based Aggregator Engine
    Aggregates only trusted model updates weighted by normalized Trust Scores.
    Excluded hospitals (Trust < 40) or suspicious updates are filtered out.
    """

    def aggregate_weights(
        self,
        updates: List[Tuple[List[np.ndarray], int, float, str]], # (weights, sample_count, trust_score, hospital_id)
        min_trust_threshold: float = 40.0
    ) -> List[np.ndarray]:
        """
        Performs trust-weighted average over valid client parameters.
        """
        valid_updates = [u for u in updates if u[2] >= min_trust_threshold]

        if not valid_updates:
            # Fallback if all excluded: return average of highest trust update
            valid_updates = sorted(updates, key=lambda x: x[2], reverse=True)[:1]

        total_weight = sum(sample_cnt * (trust / 100.0) for _, sample_cnt, trust, _ in valid_updates) + 1e-8

        # Initialize global weight accumulation structure
        first_weights = valid_updates[0][0]
        aggregated_weights = [np.zeros_like(w, dtype=np.float32) for w in first_weights]

        for weights, sample_cnt, trust, hid in valid_updates:
            alpha = (sample_cnt * (trust / 100.0)) / total_weight
            for i, layer_weight in enumerate(weights):
                aggregated_weights[i] += alpha * layer_weight.astype(np.float32)

        return aggregated_weights

import numpy as np
import torch
from typing import Dict, List, Any, Tuple

class TrustEngine:
    """
    Step 10: Trust-Based Aggregation Engine Core
    Computes statistical indicators across client parameter updates:
    - Cosine Similarity
    - Euclidean Distance
    - Gradient Norm
    - Layer-wise Similarity
    - Parameter Variance
    - Historical Consistency
    - Z-Score normalization
    Flagging Z < -1.5 as suspicious and adjusting dynamic Trust Scores.
    """

    SUSPICIOUS_Z_THRESHOLD = -1.5
    EXCLUSION_TRUST_THRESHOLD = 40.0

    def compute_client_metrics(
        self,
        client_weights: List[np.ndarray],
        global_weights: List[np.ndarray],
        historical_scores: List[float] = None
    ) -> Dict[str, float]:
        """
        Computes metric set for a single client update relative to the global model state.
        """
        # Vectorize parameters
        client_vec = np.concatenate([p.flatten() for p in client_weights])
        global_vec = np.concatenate([p.flatten() for p in global_weights])

        # 1. Cosine Similarity
        norm_c = np.linalg.norm(client_vec) + 1e-8
        norm_g = np.linalg.norm(global_vec) + 1e-8
        cosine_sim = float(np.dot(client_vec, global_vec) / (norm_c * norm_g))

        # 2. Euclidean Distance
        euclidean_dist = float(np.linalg.norm(client_vec - global_vec))

        # 3. Gradient Norm (approximate parameter update delta norm)
        grad_norm = float(np.linalg.norm(client_vec - global_vec))

        # 4. Parameter Variance
        param_var = float(np.var(client_vec - global_vec))

        # 5. Layer-wise Similarity (mean cosine similarity across first 3 layers)
        layer_sims = []
        for i in range(min(len(client_weights), 4)):
            c_layer = client_weights[i].flatten()
            g_layer = global_weights[i].flatten()
            l_norm_c = np.linalg.norm(c_layer) + 1e-8
            l_norm_g = np.linalg.norm(g_layer) + 1e-8
            layer_sims.append(np.dot(c_layer, g_layer) / (l_norm_c * l_norm_g))
        layer_wise_sim = float(np.mean(layer_sims)) if layer_sims else cosine_sim

        # 6. Historical Consistency
        hist_consistency = float(np.mean(historical_scores)) if historical_scores else 100.0

        return {
            "cosine_similarity": cosine_sim,
            "euclidean_distance": euclidean_dist,
            "gradient_norm": grad_norm,
            "parameter_variance": param_var,
            "layer_wise_similarity": layer_wise_sim,
            "historical_consistency": hist_consistency
        }

    def evaluate_round_trust(
        self,
        hospital_updates: Dict[str, Dict[str, Any]],
        current_trust_scores: Dict[str, float]
    ) -> Tuple[Dict[str, Dict[str, Any]], Dict[str, float]]:
        """
        Evaluates Z-Scores across all participating hospital updates for the round.
        Returns detailed trust metrics per hospital and updated trust scores.
        """
        hospital_ids = list(hospital_updates.keys())
        if not hospital_ids:
            return {}, current_trust_scores

        cosine_sims = [hospital_updates[hid]["metrics"]["cosine_similarity"] for hid in hospital_ids]

        # Calculate Z-Scores for Cosine Similarity
        mean_sim = np.mean(cosine_sims)
        std_sim = np.std(cosine_sims) + 1e-6
        z_scores = [(sim - mean_sim) / std_sim for sim in cosine_sims]

        updated_trust = current_trust_scores.copy()
        round_results = {}

        for i, hid in enumerate(hospital_ids):
            z_score = float(z_scores[i])
            curr_score = updated_trust.get(hid, 100.0)
            is_suspicious = z_score < self.SUSPICIOUS_Z_THRESHOLD
            
            # Additional attack flag check from hospital payload if simulated
            if hospital_updates[hid].get("is_attack_active", False):
                is_suspicious = True

            if is_suspicious:
                new_score = max(0.0, curr_score - 15.0)
                status = "Suspicious" if new_score >= self.EXCLUSION_TRUST_THRESHOLD else "Excluded"
                reason = f"Anomalous gradient update detected (Z-Score: {z_score:.2f} < -1.5)"
            else:
                new_score = min(100.0, curr_score + 5.0)
                status = "Active" if new_score >= self.EXCLUSION_TRUST_THRESHOLD else "Excluded"
                reason = "Verified honest update"

            updated_trust[hid] = new_score

            round_results[hid] = {
                "z_score": z_score,
                "is_suspicious": is_suspicious,
                "previous_trust_score": curr_score,
                "new_trust_score": new_score,
                "status": status,
                "reason": reason,
                "metrics": hospital_updates[hid]["metrics"]
            }

        return round_results, updated_trust

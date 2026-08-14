import torch
import torch.nn as nn
import torch.nn.functional as F

class MultimodalFeatureFusionEngine(nn.Module):
    """
    Step 7: Multimodal Feature Fusion Engine
    Fuses high-dimensional feature vectors from CNN (Vision), ANN (Tabular), and BERT (Text).
    Uses Cross-Attention & Gated Multi-Head Attention Fusion to produce a Unified Patient Representation.
    """
    def __init__(self, embed_dim: int = 128, num_heads: int = 4, num_classes: int = 2):
        super(MultimodalFeatureFusionEngine, self).__init__()
        self.embed_dim = embed_dim
        
        # Self & Cross Multi-head attention across 3 modalities [CNN, ANN, BERT]
        self.multihead_attn = nn.MultiheadAttention(embed_dim=embed_dim, num_heads=num_heads, batch_first=True)
        
        # Gated fusion projection
        self.fusion_fc1 = nn.Linear(embed_dim * 3, embed_dim * 2)
        self.fusion_fc2 = nn.Linear(embed_dim * 2, embed_dim)
        self.bn = nn.BatchNorm1d(embed_dim)
        
        # Final Diagnosis / Risk Prediction Head (2 classes: Low Risk vs High Risk)
        self.global_diagnostic_head = nn.Linear(embed_dim, num_classes)


    def forward(self, cnn_embed: torch.Tensor, ann_embed: torch.Tensor, bert_embed: torch.Tensor):
        # Input shape for each: [B, embed_dim]
        # Stack modalities to sequence format [B, 3, embed_dim]
        stacked = torch.stack([cnn_embed, ann_embed, bert_embed], dim=1)
        
        # Cross-Attention over modalities
        attn_out, attn_weights = self.multihead_attn(query=stacked, key=stacked, value=stacked) # [B, 3, embed_dim]
        
        # Flatten attention outputs
        flattened_attn = attn_out.reshape(attn_out.size(0), -1) # [B, embed_dim * 3]
        
        # Gated MLP projection
        h = F.relu(self.fusion_fc1(flattened_attn))
        unified_representation = self.bn(F.relu(self.fusion_fc2(h))) # [B, embed_dim]
        
        logits = self.global_diagnostic_head(unified_representation)

        return {
            "unified_representation": unified_representation,
            "logits": logits,
            "attention_weights": attn_weights, # [B, 3, 3] modality interaction matrix
            "modality_breakdown": {
                "cnn_weight": float(torch.mean(attn_weights[:, 0, :]).item()),
                "ann_weight": float(torch.mean(attn_weights[:, 1, :]).item()),
                "bert_weight": float(torch.mean(attn_weights[:, 2, :]).item())
            }
        }

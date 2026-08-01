import torch
import torch.nn as nn
import torch.nn.functional as F

class ClinicalBERTModule(nn.Module):
    """
    Step 6: BERT Module for Clinical Text & Reports
    Processes Doctor Notes, Prescriptions, Summaries.
    Outputs Text Feature Vector (128-d) and Clinical Intent Logits.
    """
    def __init__(self, vocab_size: int = 5000, max_seq_len: int = 128, embed_dim: int = 128):
        super(ClinicalBERTModule, self).__init__()
        self.token_embedding = nn.Embedding(vocab_size, 64)
        self.pos_embedding = nn.Embedding(max_seq_len, 64)
        
        encoder_layer = nn.TransformerEncoderLayer(d_model=64, nhead=4, batch_first=True)
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=2)
        
        self.fc_embed = nn.Linear(64, embed_dim)
        self.ner_head = nn.Linear(embed_dim, 8) # 8 NER entity categories

    def forward(self, input_ids: torch.Tensor):
        # input_ids: [B, seq_len]
        seq_len = input_ids.size(1)
        positions = torch.arange(0, seq_len, device=input_ids.device).unsqueeze(0).repeat(input_ids.size(0), 1)
        
        x = self.token_embedding(input_ids) + self.pos_embedding(positions) # [B, seq_len, 64]
        out = self.transformer_encoder(x) # [B, seq_len, 64]
        
        # Mean pooling across tokens
        pooled = torch.mean(out, dim=1) # [B, 64]
        embeddings = F.relu(self.fc_embed(pooled)) # [B, embed_dim]
        ner_logits = self.ner_head(embeddings)

        return {
            "embeddings": embeddings,
            "ner_logits": ner_logits
        }

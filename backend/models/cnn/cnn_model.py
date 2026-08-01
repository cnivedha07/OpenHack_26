import torch
import torch.nn as nn
import torch.nn.functional as F

class MedicalCNNModule(nn.Module):
    """
    Step 4: CNN Module for Medical Images
    Processes Chest X-Rays, MRIs, CT Scans, ECGs.
    Outputs high-dimensional image feature vector (128-d) and attention maps.
    """
    def __init__(self, embed_dim: int = 128):
        super(MedicalCNNModule, self).__init__()
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, stride=1, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, stride=1, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, stride=1, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.adaptive_pool = nn.AdaptiveAvgPool2d((4, 4))
        
        # Linear projection layer for embedding
        self.fc_embed = nn.Linear(128 * 4 * 4, embed_dim)
        # Auxiliary classifier head for disease detection (e.g., Pneumonia, Tumor, Normal)
        self.classifier = nn.Linear(embed_dim, 4)

    def forward(self, x: torch.Tensor):
        # x shape: [B, 3, H, W]
        x = F.relu(self.bn1(self.conv1(x)))
        x = self.pool(x)
        x = F.relu(self.bn2(self.conv2(x)))
        x = self.pool(x)
        x = F.relu(self.bn3(self.conv3(x)))
        
        # Spatial attention map generation
        attention_map = torch.mean(x, dim=1, keepdim=True) # [B, 1, H', W']
        attention_map = F.softmax(attention_map.view(x.size(0), -1), dim=-1).view_as(attention_map)
        
        x = self.adaptive_pool(x)
        flattened = x.view(x.size(0), -1)
        
        embeddings = F.relu(self.fc_embed(flattened)) # [B, embed_dim]
        logits = self.classifier(embeddings) # [B, 4]
        
        return {
            "embeddings": embeddings,
            "logits": logits,
            "attention_map": attention_map
        }

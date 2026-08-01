import torch
import torch.nn as nn
import torch.nn.functional as F

class MedicalANNModule(nn.Module):
    """
    Step 5: ANN Module for Tabular & Numerical Records
    Processes Blood Pressure, Sugar, Heart Rate, SpO2, BMI, Hemoglobin, Platelets, Age, Weight, Temp.
    Predicts Disease Risk, Mortality Risk, Readmission Risk, and Severity Score.
    """
    def __init__(self, input_features: int = 10, embed_dim: int = 128):
        super(MedicalANNModule, self).__init__()
        self.fc1 = nn.Linear(input_features, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.fc2 = nn.Linear(64, 128)
        self.bn2 = nn.BatchNorm1d(128)
        
        self.fc_embed = nn.Linear(128, embed_dim)
        
        # Risk prediction heads
        self.disease_risk_head = nn.Linear(embed_dim, 1) # Sigmoid probability
        self.mortality_risk_head = nn.Linear(embed_dim, 1)
        self.readmission_risk_head = nn.Linear(embed_dim, 1)
        self.severity_score_head = nn.Linear(embed_dim, 1) # 0 to 10 score

    def forward(self, x: torch.Tensor):
        # x shape: [B, input_features]
        h = F.relu(self.bn1(self.fc1(x)))
        h = F.relu(self.bn2(self.fc2(h)))
        
        embeddings = F.relu(self.fc_embed(h)) # [B, embed_dim]
        
        disease_risk = torch.sigmoid(self.disease_risk_head(embeddings))
        mortality_risk = torch.sigmoid(self.mortality_risk_head(embeddings))
        readmission_risk = torch.sigmoid(self.readmission_risk_head(embeddings))
        severity_score = torch.clamp(self.severity_score_head(embeddings), 0.0, 10.0)

        return {
            "embeddings": embeddings,
            "disease_risk": disease_risk,
            "mortality_risk": mortality_risk,
            "readmission_risk": readmission_risk,
            "severity_score": severity_score
        }

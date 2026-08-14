import pytest
import numpy as np
import torch
import flwr as fl
from fastapi.testclient import TestClient
from main import app
from database.database import init_db, SessionLocal
from database.models import RoundLogModel, GlobalModelVersionModel
from federated.data_loader import get_hospital_dataloader
from federated.client.flower_client import HospitalFLClient
from federated.server.flower_server import FederatedServerManager

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_fl_env():
    init_db()


def get_admin_headers():
    login_res = client.post("/auth/admin/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_flower_and_pytorch_imports():
    assert hasattr(fl.client, "NumPyClient")
    assert hasattr(fl.server.strategy, "FedAvg")


def test_data_loader_multimodal_tensors():
    dataloader = get_hospital_dataloader("hospital_1", batch_size=4, shuffle=False)
    assert dataloader is not None
    
    for img, tab, text, targets in dataloader:
        assert img.shape == torch.Size([4, 3, 64, 64])
        assert tab.shape == torch.Size([4, 8])
        assert text.shape[0] == 4
        assert targets.shape[0] == 4
        break


def test_local_pytorch_training_updates_parameters():
    h_client = HospitalFLClient("hospital_1", sample_count=50)
    initial_params = [p.copy() for p in h_client.get_parameters()]

    # Execute 1 epoch of PyTorch backpropagation over local DataLoader
    updated_weights, num_samples, metrics = h_client.train_local_epoch(initial_params)

    assert len(updated_weights) == len(initial_params)
    assert num_samples > 0
    assert "train_loss" in metrics
    assert "val_accuracy" in metrics

    # Verify parameters actually changed due to loss.backward() and optimizer.step()
    params_changed = False
    for p_init, p_upd in zip(initial_params, updated_weights):
        if not np.allclose(p_init, p_upd, atol=1e-5):
            params_changed = True
            break
    assert params_changed is True, "PyTorch parameters must change after local gradient step"


def test_5_federated_rounds_execution_and_persistence():
    headers = get_admin_headers()
    # Reset training state to start clean from round 0
    client.post("/train/reset", headers=headers)
    initial_losses = []
    
    # Execute 5 federated rounds via API
    for r in range(1, 6):
        res = client.post("/train/start", headers=headers)
        assert res.status_code == 200
        summary = res.json()["round_summary"]
        assert summary["round_number"] == r
        initial_losses.append(summary["global_loss"])


    # Verify DB persistence of all 5 rounds
    db = SessionLocal()
    try:
        round_logs = db.query(RoundLogModel).all()
        assert len(round_logs) >= 20 # 4 hospitals x 5 rounds

        global_versions = db.query(GlobalModelVersionModel).all()
        assert len(global_versions) >= 5
    finally:
        db.close()


def test_fusion_endpoint_returns_dynamic_attention_weights():
    headers = get_admin_headers()

    res = client.get("/fusion", headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert "weights_distribution" in data
    dist = data["weights_distribution"]
    assert "CNN (Vision)" in dist
    assert "ANN (Tabular)" in dist
    assert "BERT (Text)" in dist
    # Sum of modality weights should equal ~100%
    total_weight = dist["CNN (Vision)"] + dist["ANN (Tabular)"] + dist["BERT (Text)"]
    assert abs(total_weight - 100.0) < 1.0

import os
import pytest
import pandas as pd
import numpy as np
import torch
from fastapi.testclient import TestClient
from main import app
from database.database import init_db
from federated.data_loader import MultimodalHealthcareDataset, get_hospital_dataloader
from federated.client.flower_client import HospitalFLClient

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_skewed_hospital(tmp_path_factory):
    init_db()
    # Create temporary directory with a highly skewed dataset (95% Low Risk, 5% High Risk)
    tmp_dir = tmp_path_factory.mktemp("skewed_data")
    hosp_dir = tmp_dir / "hospital_skewed"
    hosp_dir.mkdir(parents=True, exist_ok=True)

    num_samples = 200
    num_high_risk = 10 # 5% minority class
    num_low_risk = 190 # 95% majority class

    labels = [0] * num_low_risk + [1] * num_high_risk
    
    # Skewed vitals features
    bp = [110] * num_low_risk + [160] * num_high_risk
    o2 = [98.0] * num_low_risk + [91.0] * num_high_risk
    sugar = [90] * num_low_risk + [210] * num_high_risk
    bmi = [22.0] * num_low_risk + [34.0] * num_high_risk

    df = pd.DataFrame({
        "patient_id": [f"P-SKEW{idx:04d}" for idx in range(num_samples)],
        "patient_name": [f"Patient_{idx}" for idx in range(num_samples)],
        "aadhaar_number": ["1234-5678-9012"] * num_samples,
        "age": [45] * num_samples,
        "blood_pressure": bp,
        "heart_rate": [75] * num_samples,
        "oxygen_saturation": o2,
        "blood_sugar": sugar,
        "bmi": bmi,
        "hemoglobin": [14.0] * num_samples,
        "platelets": [250000] * num_samples,
        "doctor_notes": ["Patient routine checkup."] * num_samples,
        "risk_level": labels
    })
    df.to_csv(hosp_dir / "vitals_data.csv", index=False)
    return str(tmp_dir)


def get_admin_headers():
    login_res = client.post("/auth/admin/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_inverse_frequency_class_weight_calculation(setup_skewed_hospital):
    csv_path = os.path.join(setup_skewed_hospital, "hospital_skewed", "vitals_data.csv")
    ds = MultimodalHealthcareDataset(csv_path=csv_path)

    weights = ds.get_class_weights()
    assert isinstance(weights, torch.Tensor)
    assert weights.shape == torch.Size([2])
    # Minority class weight (class 1) must be significantly higher than majority class weight (class 0)
    assert weights[1] > weights[0]
    assert weights[1] / weights[0] > 10.0 # ~190/10 = 19x higher weight


def test_class_weighting_improves_minority_recall(setup_skewed_hospital):
    skewed_dir = setup_skewed_hospital
    csv_path = os.path.join(skewed_dir, "hospital_skewed", "vitals_data.csv")

    # 1. Train WITHOUT class weighting
    client_no_weights = HospitalFLClient("hospital_skewed", sample_count=200)
    client_no_weights.dataloader = get_hospital_dataloader("hospital_skewed", batch_size=16, shuffle=False, data_dir=skewed_dir)
    client_no_weights.use_class_weighting = False
    
    global_params = client_no_weights.get_parameters()
    
    # Train 3 epochs without class weighting
    for _ in range(3):
        client_no_weights.train_local_epoch(global_params)
    metrics_no_weights = client_no_weights.last_metrics
    recall_unweighted = metrics_no_weights.get("recall_class_1", 0.0)

    # 2. Train WITH inverse-frequency class weighting
    client_with_weights = HospitalFLClient("hospital_skewed", sample_count=200)
    client_with_weights.dataloader = get_hospital_dataloader("hospital_skewed", batch_size=16, shuffle=False, data_dir=skewed_dir)
    client_with_weights.use_class_weighting = True

    # Train 3 epochs with class weighting
    for _ in range(3):
        client_with_weights.train_local_epoch(global_params)
    metrics_weighted = client_with_weights.last_metrics
    recall_weighted = metrics_weighted.get("recall_class_1", 0.0)

    # Verify minority class recall is higher or equal with weighting enabled
    assert recall_weighted >= recall_unweighted
    assert metrics_weighted["use_class_weighting"] is True
    assert "class_distribution" in metrics_weighted
    assert metrics_weighted["class_distribution"]["class_1_ratio"] == 0.05


def test_fit_report_exposes_per_class_metrics():
    headers = get_admin_headers()

    # Execute 1 training round to populate metrics
    client.post("/train/start", headers=headers)

    res = client.get("/train/fit-report", headers=headers)
    assert res.status_code == 200
    hospitals = res.json()["hospitals"]
    assert "hospital_1" in hospitals
    h1 = hospitals["hospital_1"]

    assert "precision_class_0" in h1
    assert "recall_class_0" in h1
    assert "precision_class_1" in h1
    assert "recall_class_1" in h1
    assert "minority_class_recall" in h1
    assert "class_distribution" in h1
    assert "use_class_weighting" in h1
    assert "fedprox_mu" in h1

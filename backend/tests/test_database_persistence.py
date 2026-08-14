import pytest
from fastapi.testclient import TestClient
from main import app
from database.database import init_db, get_db, SessionLocal
from database.models import PrivacyAuditModel, RoundLogModel, GlobalModelVersionModel, AttackLogModel

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_db():
    init_db()


def get_admin_headers():
    login_res = client.post("/auth/admin/login", json={"username": "admin", "password": "admin123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def get_hospital_headers(hosp_user="hospital_1_user", hosp_pass="hospital123"):
    login_res = client.post("/auth/hospital/login", json={"username": hosp_user, "password": hosp_pass})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_creates_privacy_audit_log():
    headers = get_hospital_headers("hospital_1_user")
    file_content = b"Patient John Doe Aadhaar: 1234 5678 9012 Phone: +919876543210"
    
    response = client.post(
        "/upload",
        data={"hospital_id": "hospital_1"},
        files={"file": ("clinical_note.txt", file_content, "text/plain")},
        headers=headers
    )
    assert response.status_code == 200

    # Query DB to verify persistence
    db = SessionLocal()
    try:
        audit = db.query(PrivacyAuditModel).filter_by(hospital_id="hospital_1", filename="clinical_note.txt").first()
        assert audit is not None
        assert audit.data_type == "Text"
        assert len(audit.entities_detected) > 0
    finally:
        db.close()


def test_training_round_creates_round_and_global_model_logs():
    headers = get_admin_headers()
    
    response = client.post("/train/start", headers=headers)
    assert response.status_code == 200
    summary = response.json()["round_summary"]
    current_round = summary["round_number"]

    # Query DB to verify round logs
    db = SessionLocal()
    try:
        round_logs = db.query(RoundLogModel).filter_by(round_number=current_round).all()
        assert len(round_logs) > 0
        for log in round_logs:
            assert log.trust_score_after is not None
            assert log.cosine_similarity is not None

        global_ver = db.query(GlobalModelVersionModel).filter_by(round_number=current_round).first()
        assert global_ver is not None
        assert global_ver.version == f"v2.{current_round}.0"
        assert len(global_ver.participating_hospitals) > 0
    finally:
        db.close()


def test_attack_toggle_creates_attack_log():
    headers = get_admin_headers()

    response = client.post(
        "/attack/toggle",
        json={"hospital_id": "hospital_3", "attack_type": "Label Flip", "intensity": 1.0},
        headers=headers
    )
    assert response.status_code == 200

    # Query DB to verify attack log
    db = SessionLocal()
    try:
        attack_log = db.query(AttackLogModel).filter_by(attacker_hospital_id="hospital_3", attack_type="Label Flip").first()
        assert attack_log is not None
        assert attack_log.detected is True
        assert attack_log.trust_penalty == 15.0
    finally:
        db.close()


def test_privacy_status_reflects_db_records():
    headers = get_hospital_headers()
    
    status_res = client.get("/privacy/status", headers=headers)
    assert status_res.status_code == 200
    data = status_res.json()
    
    assert data["total_anonymized_files"] >= 1
    assert data["pii_redacted_count"] >= 1


def test_logs_endpoint_returns_live_logs():
    headers = get_admin_headers()

    response = client.get("/logs", headers=headers)
    assert response.status_code == 200
    logs = response.json()["logs"]
    assert isinstance(logs, list)
    assert len(logs) > 0

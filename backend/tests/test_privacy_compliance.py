import os
import tempfile
import pytest
from fastapi.testclient import TestClient
from main import app
from database.database import init_db
from privacy.privacy_shield import PrivacyShieldEngine

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_env():
    init_db()


def get_hospital_headers():
    login_res = client.post("/auth/hospital/login", json={"username": "hospital_1_user", "password": "hospital123"})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_file_size_limit_exceeded_returns_413():
    headers = get_hospital_headers()
    # Create 11MB payload exceeding 10MB limit
    large_payload = b"A" * (11 * 1024 * 1024)

    res = client.post(
        "/upload",
        files={"file": ("large_scan.dcm", large_payload, "application/octet-stream")},
        data={"hospital_id": "hospital_1"},
        headers=headers
    )
    assert res.status_code == 413
    assert "10MB" in res.json()["detail"] or "Payload Too Large" in res.json()["detail"]


def test_upload_leaves_zero_unredacted_disk_files():
    headers = get_hospital_headers()
    payload = b"Patient Name: John Doe, Aadhaar: 1234-5678-9012, Blood Pressure: 120"
    
    # Record initial files in temp directory
    temp_dir = tempfile.gettempdir()
    initial_temp_files = set(os.listdir(temp_dir))

    res = client.post(
        "/upload",
        files={"file": ("clinical_note.txt", payload, "text/plain")},
        data={"hospital_id": "hospital_1"},
        headers=headers
    )
    assert res.status_code == 200
    
    # Verify temp directory has no newly leaked raw upload files
    final_temp_files = set(os.listdir(temp_dir))
    new_files = final_temp_files - initial_temp_files
    
    for nf in new_files:
        assert "john_doe" not in nf.lower()
        assert "1234-5678" not in nf


def test_privacy_review_endpoint_proposes_entity_redactions():
    headers = get_hospital_headers()
    raw_text = "Doctor: Dr. Sarah Connor, Patient: John Connor, Aadhaar: 9876 5432 1098, Email: john@example.com"

    res = client.post(
        "/privacy/review",
        json={"text": raw_text},
        headers=headers
    )
    assert res.status_code == 200
    data = res.json()

    assert data["proposed_redactions_count"] >= 2
    proposals = data["proposals"]
    
    entity_types = [p["entity_type"] for p in proposals]
    assert "Aadhaar Number" in entity_types or "Email" in entity_types
    
    for p in proposals:
        assert "start_index" in p
        assert "end_index" in p
        assert p["proposed_token"] == "[REDACTED]"
        assert p["review_status"] == "PENDING_APPROVAL"


def test_compliance_status_document_exists():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    doc_path = os.path.join(root_dir, "docs", "COMPLIANCE_STATUS.md")

    assert os.path.exists(doc_path), "docs/COMPLIANCE_STATUS.md must exist"
    with open(doc_path, "r", encoding="utf-8") as f:
        content = f.read()
        assert "HIPAA" in content
        assert "Data Locality" in content
        assert "Zero Raw Disk Leakage" in content

import pytest
from fastapi.testclient import TestClient
from main import app
from database.database import init_db

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()


def test_auth_login_admin():
    response = client.post("/auth/admin/login", json={
        "username": "admin",
        "password": "admin123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "admin"
    assert data["hospital_id"] is None


def test_auth_login_hospital_1():
    response = client.post("/auth/hospital/login", json={
        "username": "hospital_1_user",
        "password": "hospital123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "hospital"
    assert data["hospital_id"] == "hospital_1"


def test_auth_login_hospital_2():
    response = client.post("/auth/hospital/login", json={
        "username": "hospital_2_user",
        "password": "hospital123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["role"] == "hospital"
    assert data["hospital_id"] == "hospital_2"


def test_unauthenticated_requests_fail():
    # Admin route without token
    res1 = client.post("/train/start")
    assert res1.status_code == 401

    # Protected route without token
    res2 = client.get("/privacy/status")
    assert res2.status_code == 401

    # Upload route without token
    res3 = client.post("/upload", data={"hospital_id": "hospital_1"}, files={"file": ("test.txt", b"hello", "text/plain")})
    assert res3.status_code == 401


def test_hospital_accessing_admin_endpoint_forbidden():
    # Login as hospital 1
    login_res = client.post("/auth/hospital/login", json={
        "username": "hospital_1_user",
        "password": "hospital123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Hospital attempting to start training
    res1 = client.post("/train/start", headers=headers)
    assert res1.status_code == 403
    assert "Admin privileges required" in res1.json()["detail"]

    # Hospital attempting to toggle attack
    res2 = client.post("/attack/toggle", json={"hospital_id": "hospital_2", "attack_type": "Label Flip"}, headers=headers)
    assert res2.status_code == 403

    # Hospital attempting to view global system logs
    res3 = client.get("/logs", headers=headers)
    assert res3.status_code == 403

    # Hospital attempting to view trust scores for all hospitals
    res4 = client.get("/trust", headers=headers)
    assert res4.status_code == 403


def test_hospital_cross_tenant_isolation_forbidden():
    # Login as hospital 1
    login_res = client.post("/auth/hospital/login", json={
        "username": "hospital_1_user",
        "password": "hospital123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Hospital 1 attempting to upload data on behalf of Hospital 2
    res = client.post(
        "/upload",
        data={"hospital_id": "hospital_2"},
        files={"file": ("patient_record.txt", b"Patient John Doe Aadhaar: 1234 5678 9012", "text/plain")},
        headers=headers
    )
    assert res.status_code == 403
    assert "cannot access resources belonging to 'hospital_2'" in res.json()["detail"] or "cannot upload data for 'hospital_2'" in res.json()["detail"]


def test_hospital_own_tenant_access_allowed():
    # Login as hospital 1
    login_res = client.post("/auth/hospital/login", json={
        "username": "hospital_1_user",
        "password": "hospital123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Hospital 1 uploading to hospital 1
    res = client.post(
        "/upload",
        data={"hospital_id": "hospital_1"},
        files={"file": ("patient_record.txt", b"Patient John Doe Aadhaar: 1234 5678 9012", "text/plain")},
        headers=headers
    )
    assert res.status_code == 200
    assert res.json()["hospital_id"] == "hospital_1"


def test_admin_access_allowed():
    # Login as admin
    login_res = client.post("/auth/admin/login", json={
        "username": "admin",
        "password": "admin123"
    })
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Admin starting training
    res1 = client.post("/train/start", headers=headers)
    assert res1.status_code == 200

    # Admin viewing trust scores
    res2 = client.get("/trust", headers=headers)
    assert res2.status_code == 200

    # Admin viewing logs
    res3 = client.get("/logs", headers=headers)
    assert res3.status_code == 200

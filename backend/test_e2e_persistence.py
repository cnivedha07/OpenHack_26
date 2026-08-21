import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("--- STEP 1: Admin Login ---")
    login_res = requests.post(f"{BASE_URL}/auth/admin/login", json={"username": "admin", "password": "admin123"})
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Admin Token Acquired Successfully.")

    print("\n--- STEP 2: Dataset Upload & Local Training Trigger ---")
    csv_content = (
        "patient_id,age,blood_pressure,cholesterol,doctor_notes,risk_level\n"
        "P-101,54,135,210,Patient Ramesh Kumar (Aadhaar: 4829-1039-5820) reports chest tightness,1\n"
        "P-102,62,145,240,Patient Sunita Sharma DOB 14/05/1978 shows elevated blood pressure,1\n"
        "P-103,41,120,180,Routine checkup for Rahul Verma phone +91 98450 12345 normal findings,0\n"
    )

    files = {"file": ("patient_records_hosp1.csv", csv_content.encode("utf-8"), "text/csv")}
    data = {"hospital_id": "hospital_1"}

    upload_res = requests.post(f"{BASE_URL}/upload", files=files, data=data, headers=headers)
    assert upload_res.status_code == 200, f"Upload failed: {upload_res.text}"
    res_data = upload_res.json()
    
    print(f"Dataset ID Saved: #{res_data['dataset_id']}")
    print(f"Status: {res_data['status']}")
    print(f"PII Tokens Scrubbed: {len(res_data['privacy_shield']['redaction_audit'])}")
    print(f"Training Run Acc: {res_data['training_run']['accuracy']:.4f}, Loss: {res_data['training_run']['loss']:.4f}, F1: {res_data['training_run']['f1_score']:.4f}")

    print("\n--- STEP 3: Querying Stored Datasets & Training Runs in DB ---")
    ds_res = requests.get(f"{BASE_URL}/datasets/hospital_1", headers=headers)
    tr_res = requests.get(f"{BASE_URL}/training/runs/hospital_1", headers=headers)
    
    datasets = ds_res.json()["datasets"]
    training_runs = tr_res.json()["runs"]
    
    print(f"Total Datasets in DB for hospital_1: {len(datasets)}")
    print(f"Total Training Runs in DB for hospital_1: {len(training_runs)}")
    
    assert len(datasets) > 0, "No datasets returned from DB!"
    assert len(training_runs) > 0, "No training runs returned from DB!"
    print("\n--- E2E VERIFICATION CLEANLY PASSED! ---")

if __name__ == "__main__":
    run_test()

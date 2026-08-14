import os
import json
import pandas as pd
import numpy as np

def generate_synthetic_hospital_datasets(output_dir: str):
    """
    Generates synthetic medical datasets (CSVs, JSON FHIR, and Clinical Notes)
    for Hospitals 1 through 4.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    np.random.seed(42)
    
    for i in range(1, 5):
        hosp_dir = os.path.join(output_dir, f"hospital_{i}")
        os.makedirs(hosp_dir, exist_ok=True)

        # 1. Synthetic CSV Vitals dataset
        num_samples = 150 + i * 20
        # Compute target label: risk_level (0 = Low Risk, 1 = High Risk) based on clinical thresholds
        bp = np.random.randint(90, 160, size=num_samples)
        hr = np.random.randint(60, 110, size=num_samples)
        o2 = np.random.uniform(92.0, 99.9, size=num_samples).round(1)
        sugar = np.random.randint(70, 240, size=num_samples)
        bmi = np.random.uniform(18.5, 34.0, size=num_samples).round(1)

        # Risk formula: High risk if multiple elevated vitals
        risk_score = (bp > 135).astype(int) + (o2 < 95.0).astype(int) + (sugar > 160).astype(int) + (bmi > 30.0).astype(int)
        risk_level = (risk_score >= 1).astype(int)

        notes_templates = [
            "Patient Name: {name}, Aadhaar: {aadhaar}. Complaining of acute chest pain and dyspnea. Dr. Sharma attending.",
            "Patient Name: {name}, Aadhaar: {aadhaar}. Routine health checkup. Vitals within normal limits. Dr. Gupta attending.",
            "Patient Name: {name}, Aadhaar: {aadhaar}. Admitted with elevated blood pressure and severe fatigue. Dr. Patel attending.",
            "Patient Name: {name}, Aadhaar: {aadhaar}. Follow-up consultation for type-2 diabetes management. Dr. Rao attending.",
            "Patient Name: {name}, Aadhaar: {aadhaar}. Mild fever and body ache observed. Prescribed antipyretics. Dr. Singh attending."
        ]

        patient_names = [f"Patient_{idx}" for idx in range(num_samples)]
        aadhaar_nums = [f"{np.random.randint(1000,9999)}-{np.random.randint(1000,9999)}-{np.random.randint(1000,9999)}" for _ in range(num_samples)]

        notes_list = [
            notes_templates[idx % len(notes_templates)].format(name=patient_names[idx], aadhaar=aadhaar_nums[idx])
            for idx in range(num_samples)
        ]

        df = pd.DataFrame({
            "patient_id": [f"P-{i}{idx:04d}" for idx in range(num_samples)],
            "patient_name": patient_names,
            "aadhaar_number": aadhaar_nums,
            "age": np.random.randint(18, 85, size=num_samples),
            "blood_pressure": bp,
            "heart_rate": hr,
            "oxygen_saturation": o2,
            "blood_sugar": sugar,
            "bmi": bmi,
            "hemoglobin": np.random.uniform(11.0, 16.5, size=num_samples).round(1),
            "platelets": np.random.randint(150000, 450000, size=num_samples),
            "doctor_notes": notes_list,
            "risk_level": risk_level
        })

        csv_path = os.path.join(hosp_dir, "vitals_data.csv")
        df.to_csv(csv_path, index=False)


        # 2. Synthetic FHIR JSON
        fhir_data = {
            "resourceType": "Bundle",
            "type": "collection",
            "hospital": f"Hospital {i}",
            "entry": [
                {
                    "resource": {
                        "resourceType": "Patient",
                        "id": f"FHIR-P{i}01",
                        "name": [{"family": "Sharma", "given": ["Amit"]}],
                        "telecom": [{"system": "phone", "value": "+91 9876543210"}],
                        "gender": "male",
                        "birthDate": "1985-04-12"
                    }
                }
            ]
        }
        json_path = os.path.join(hosp_dir, "fhir_record.json")
        with open(json_path, "w") as f:
            json.dump(fhir_data, f, indent=2)

    print(f"Synthetic datasets generated successfully in: {output_dir}")

if __name__ == "__main__":
    generate_synthetic_hospital_datasets("./synthetic_data")

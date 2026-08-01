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
        df = pd.DataFrame({
            "patient_id": [f"P-{i}{idx:04d}" for idx in range(num_samples)],
            "patient_name": [f"Patient_{idx}" for idx in range(num_samples)],
            "aadhaar_number": [f"{np.random.randint(1000,9999)}-{np.random.randint(1000,9999)}-{np.random.randint(1000,9999)}" for _ in range(num_samples)],
            "age": np.random.randint(18, 85, size=num_samples),
            "blood_pressure": np.random.randint(90, 160, size=num_samples),
            "heart_rate": np.random.randint(60, 110, size=num_samples),
            "oxygen_saturation": np.random.uniform(92.0, 99.9, size=num_samples).round(1),
            "blood_sugar": np.random.randint(70, 240, size=num_samples),
            "bmi": np.random.uniform(18.5, 34.0, size=num_samples).round(1),
            "hemoglobin": np.random.uniform(11.0, 16.5, size=num_samples).round(1),
            "platelets": np.random.randint(150000, 450000, size=num_samples),
            "doctor_notes": [f"Patient Name: John Doe, Aadhaar: 1234-5678-9012. Admitted with mild fever. Dr. Smith attending." for _ in range(num_samples)]
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

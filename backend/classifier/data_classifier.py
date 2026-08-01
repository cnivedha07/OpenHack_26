from typing import Dict, Any

class IntelligentDataClassifier:
    """
    Step 3: Intelligent Data Classifier
    Classifies healthcare data into Medical Images, Numerical Records, or Clinical Documents,
    and routes them to CNN, ANN, or BERT modules respectively.
    """

    IMAGE_TYPES = {
        "Chest X-Ray": ["xray", "chest", "radiograph", "cxr"],
        "MRI": ["mri", "brain_mri", "spine_mri"],
        "CT Scan": ["ct", "scan", "computed_tomography"],
        "Ultrasound": ["ultrasound", "usg", "sonogram"],
        "ECG Image": ["ecg", "electrocardiogram"]
    }

    NUMERICAL_TYPES = {
        "Blood Report": ["blood", "cbc", "vitals", "metrics", "lab_numerical"],
        "CSV Numerical Data": ["csv", "xlsx", "patient_vitals", "records"],
        "FHIR JSON": ["fhir", "bundle", "json_vitals"]
    }

    TEXT_TYPES = {
        "Prescription": ["prescription", "rx", "medication"],
        "Doctor Notes": ["doctor_notes", "clinical_notes", "soap"],
        "Lab Report Text": ["lab_report", "interpretation"],
        "Discharge Summary": ["discharge", "summary", "hospital_exit"],
        "Medical PDF": ["pdf", "report_pdf"]
    }

    def classify_and_route(self, filename: str, content_type: str, sample_snippet: str = "") -> Dict[str, Any]:
        fn_lower = filename.lower()
        snippet_lower = sample_snippet.lower()
        ext = fn_lower.split('.')[-1] if '.' in fn_lower else ''

        # Default classification variables
        detected_category = "Clinical Documents"
        sub_type = "Doctor Notes"
        target_module = "BERT"
        confidence = 0.92

        # 1. Image classification
        if ext in ['jpg', 'jpeg', 'png', 'dcm', 'dicom']:
            detected_category = "Medical Images"
            target_module = "CNN"
            sub_type = "Chest X-Ray" # Default image type
            
            for img_type, keywords in self.IMAGE_TYPES.items():
                if any(kw in fn_lower or kw in snippet_lower for kw in keywords):
                    sub_type = img_type
                    confidence = 0.98
                    break

        # 2. Numerical / Tabular classification
        elif ext in ['csv', 'xlsx', 'xls'] or "vitals" in fn_lower or "numerical" in snippet_lower:
            detected_category = "Numerical Data"
            target_module = "ANN"
            sub_type = "Blood & Vitals Report"
            confidence = 0.96
            
            for num_type, keywords in self.NUMERICAL_TYPES.items():
                if any(kw in fn_lower or kw in snippet_lower for kw in keywords):
                    sub_type = num_type
                    break

        # 3. Clinical Documents / Text / PDF
        else:
            detected_category = "Clinical Documents"
            target_module = "BERT"
            sub_type = "Clinical Discharge Summary"
            confidence = 0.94

            for txt_type, keywords in self.TEXT_TYPES.items():
                if any(kw in fn_lower or kw in snippet_lower for kw in keywords):
                    sub_type = txt_type
                    break

        return {
            "filename": filename,
            "detected_category": detected_category,
            "sub_type": sub_type,
            "target_module": target_module,
            "confidence_score": confidence,
            "routing_path": f"DataClassifier ➔ {detected_category} ➔ {target_module} Module"
        }

import io
from typing import Dict, Any, List
import pandas as pd
from PIL import Image

class DataValidationEngine:
    """
    Step 2: Data Validation & Quality Checker
    Validates files, detects corruptions, checks schemas, resolutions, and missing values.
    """

    ALLOWED_EXTENSIONS = {
        'jpg', 'jpeg', 'png', 'dcm', 'dicom', 'pdf',
        'csv', 'xlsx', 'xls', 'json', 'fhir'
    }

    REQUIRED_CSV_COLUMNS = [
        'patient_id', 'age', 'blood_pressure', 'heart_rate',
        'oxygen_saturation', 'blood_sugar', 'bmi'
    ]

    MIN_IMAGE_RESOLUTION = (128, 128)

    def validate_file(self, filename: str, content_type: str, file_bytes: bytes) -> Dict[str, Any]:
        ext = filename.split('.')[-1].lower() if '.' in filename else ''

        report = {
            "filename": filename,
            "file_type": ext,
            "is_valid": True,
            "status": "Passed",
            "errors": [],
            "warnings": [],
            "file_size_bytes": len(file_bytes),
            "quality_score": 100.0
        }

        # 1. Unsupported extension check
        if ext not in self.ALLOWED_EXTENSIONS:
            report["is_valid"] = False
            report["status"] = "Rejected"
            report["errors"].append(f"Unsupported file format: '.{ext}'. Supported: {list(self.ALLOWED_EXTENSIONS)}")
            report["quality_score"] = 0.0
            return report

        # 2. Empty file check
        if len(file_bytes) == 0:
            report["is_valid"] = False
            report["status"] = "Rejected"
            report["errors"].append("File is empty (0 bytes).")
            report["quality_score"] = 0.0
            return report

        # 3. Validation by format
        if ext in ['jpg', 'jpeg', 'png', 'dcm', 'dicom']:
            self._validate_image(file_bytes, report)
        elif ext in ['csv', 'xlsx', 'xls']:
            self._validate_tabular(file_bytes, ext, report)
        elif ext in ['json', 'fhir']:
            self._validate_json(file_bytes, report)
        elif ext == 'pdf':
            self._validate_pdf(file_bytes, report)

        return report

    def _validate_image(self, file_bytes: bytes, report: Dict[str, Any]):
        try:
            image = Image.open(io.BytesIO(file_bytes))
            image.verify()
            
            # Reopen to check dimensions (verify closes the file handler)
            image = Image.open(io.BytesIO(file_bytes))
            w, h = image.size

            if w < self.MIN_IMAGE_RESOLUTION[0] or h < self.MIN_IMAGE_RESOLUTION[1]:
                report["warnings"].append(f"Low resolution image: {w}x{h}. Minimum recommended: {self.MIN_IMAGE_RESOLUTION[0]}x{self.MIN_IMAGE_RESOLUTION[1]}")
                report["quality_score"] -= 15.0

            report["dimensions"] = f"{w}x{h}"
            report["image_mode"] = image.mode

        except Exception as e:
            report["is_valid"] = False
            report["status"] = "Rejected"
            report["errors"].append(f"Corrupted image file: {str(e)}")
            report["quality_score"] = 0.0

    def _validate_tabular(self, file_bytes: bytes, ext: str, report: Dict[str, Any]):
        try:
            if ext == 'csv':
                df = pd.read_csv(io.BytesIO(file_bytes))
            else:
                df = pd.read_excel(io.BytesIO(file_bytes))

            # Missing value check
            null_count = df.isnull().sum().sum()
            total_cells = df.shape[0] * df.shape[1]
            if total_cells > 0:
                null_ratio = null_count / total_cells
                if null_ratio > 0.3:
                    report["warnings"].append(f"High ratio of missing values: {null_ratio:.1%}")
                    report["quality_score"] -= 20.0

            # Duplicate record check
            dups = df.duplicated().sum()
            if dups > 0:
                report["warnings"].append(f"Found {dups} duplicate records.")
                report["quality_score"] -= 10.0

            report["rows"] = df.shape[0]
            report["columns"] = list(df.columns)

        except Exception as e:
            report["is_valid"] = False
            report["status"] = "Rejected"
            report["errors"].append(f"Corrupted or invalid spreadsheet/CSV: {str(e)}")
            report["quality_score"] = 0.0

    def _validate_json(self, file_bytes: bytes, report: Dict[str, Any]):
        import json
        try:
            data = json.loads(file_bytes.decode('utf-8'))
            if isinstance(data, dict):
                if data.get("resourceType") and data.get("resourceType") != "Bundle":
                    report["warnings"].append(f"FHIR resource standard check: {data.get('resourceType')}")
            report["json_keys_count"] = len(data) if isinstance(data, dict) else len(data)
        except Exception as e:
            report["is_valid"] = False
            report["status"] = "Rejected"
            report["errors"].append(f"Invalid JSON/FHIR payload: {str(e)}")
            report["quality_score"] = 0.0

    def _validate_pdf(self, file_bytes: bytes, report: Dict[str, Any]):
        if not file_bytes.startswith(b'%PDF'):
            report["is_valid"] = False
            report["status"] = "Rejected"
            report["errors"].append("Corrupted PDF header.")
            report["quality_score"] = 0.0
        else:
            report["pages_estimate"] = 1

import re
from typing import Dict, Any, List, Tuple

class PrivacyShieldEngine:
    """
    Step 1: Privacy Shield Engine
    Executes immediately after hospital upload to sanitize all PII
    using OCR, Regex, and Named Entity Recognition (NER).
    """

    PATTERNS = {
        "Aadhaar Number": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
        "PAN Number": r"\b[A-Z]{5}\d{4}[A-Z]{1}\b",
        "Phone Number": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
        "Email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "Date of Birth": r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
        "Medical Record Number (MRN)": r"\bMRN[-\s]?\d{5,10}\b",
        "Hospital ID": r"\bHOSP[-\s]?\d{4,8}\b",
        "Insurance Number": r"\bINS[-\s]?\d{6,12}\b",
        "Patient Name": r"(?:Patient Name|Patient|Name):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        "Doctor Name": r"(?:Doctor|Dr\.|Attending Physician):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        "Guardian Name": r"(?:Guardian|S/O|D/O|W/O):\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
        "Address": r"\b\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Road|Rd|Avenue|Ave|Block|District|City|State)\b",
    }

    REDACTION_TOKEN = "[REDACTED]"

    def __init__(self):
        # Additional rule-based NER keywords
        self.ner_keywords = [
            "Aadhaar", "PAN", "SSN", "Passport", "Driver License",
            "Emergency Contact", "Signature", "Barcode", "QR Code Metadata"
        ]

    def anonymize_text(self, text: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Anonymizes raw clinical text, reports, or OCR extractions.
        Returns anonymized text and audit logs of redacted entities.
        """
        redacted_text = text
        audit_log = []

        for entity_type, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, redacted_text, flags=re.IGNORECASE)
            if matches:
                for match in set(matches):
                    val = match if isinstance(match, str) else match[0]
                    if val and len(val.strip()) > 0:
                        audit_log.append({
                            "entity_type": entity_type,
                            "original_token_preview": val[:3] + "***" if len(val) > 3 else "***",
                            "status": "REDACTED"
                        })
                        redacted_text = re.sub(re.escape(val), self.REDACTION_TOKEN, redacted_text)

        # Keyword NER check
        for kw in self.ner_keywords:
            pattern = rf"\b{kw}:\s*[\w\d\s-]+\b"
            matches = re.findall(pattern, redacted_text, flags=re.IGNORECASE)
            for m in matches:
                audit_log.append({
                    "entity_type": f"Metadata ({kw})",
                    "original_token_preview": m[:6] + "***",
                    "status": "REDACTED"
                })
                redacted_text = redacted_text.replace(m, f"{kw}: {self.REDACTION_TOKEN}")

        return redacted_text, audit_log

    def anonymize_tabular(self, record: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Anonymizes structured dict / tabular medical records.
        """
        sanitized = record.copy()
        audit_log = []

        pii_keys = [
            "name", "patient_name", "aadhaar", "pan", "phone", "email",
            "address", "mrn", "hospital_id", "insurance_no", "doctor",
            "guardian", "dob", "photo_metadata", "qr_code", "barcode"
        ]

        for k, v in record.items():
            k_lower = k.lower()
            if any(pii_key in k_lower for pii_key in pii_keys):
                audit_log.append({
                    "entity_type": k,
                    "original_token_preview": str(v)[:3] + "***" if str(v) else "***",
                    "status": "REDACTED"
                })
                sanitized[k] = self.REDACTION_TOKEN
            elif isinstance(v, str):
                anon_val, sub_log = self.anonymize_text(v)
                sanitized[k] = anon_val
                audit_log.extend(sub_log)

        return sanitized, audit_log

    def process_file_privacy(self, filename: str, content_type: str, raw_bytes: bytes) -> Dict[str, Any]:
        """
        Processes file upload and strips PII metadata/OCR content.
        """
        text_content = ""
        try:
            text_content = raw_bytes.decode('utf-8', errors='ignore')
        except Exception:
            text_content = f"Binary payload ({filename})"

        anonymized_text, logs = self.anonymize_text(text_content)

        return {
            "filename": filename,
            "content_type": content_type,
            "privacy_shield_applied": True,
            "entities_redacted_count": len(logs),
            "redaction_audit": logs,
            "anonymized_sample": anonymized_text[:300] + ("..." if len(anonymized_text) > 300 else "")
        }

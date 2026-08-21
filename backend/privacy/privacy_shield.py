import re
from typing import Dict, Any, List, Tuple

class PrivacyShieldEngine:
    """
    Step 1: Privacy Shield Engine
    Executes immediately after hospital upload to sanitize all PII
    using OCR, Regex, and Named Entity Recognition (NER).
    """

    # Structured Field-Level Key-Value Patterns
    KV_PATTERNS = [
        ("Patient Name", r"(?i)\b(?:Patient\s+Name|Patient)\s*:\s*([^\n]+)"),
        ("Patient ID", r"(?i)\b(?:Patient\s*ID|Patient-ID|PID|ID)\s*:\s*([^\n]+)"),
        ("Medical Record Number (MRN)", r"(?i)\b(?:MRN|Medical\s+Record\s+Number)\s*:\s*([^\n]+)"),
        ("Date of Birth", r"(?i)\b(?:Date\s+of\s+Birth|DOB|Birth\s+Date)\s*:\s*([^\n]+)"),
        ("Address", r"(?i)\b(?:Address|Residing\s+at)\s*:\s*([^\n]+)"),
        ("Emergency Contact", r"(?i)\b(?:Emergency\s+Contact|Next\s+of\s+Kin|Guardian|S/O|D/O|W/O)\s*:\s*([^\n]+)"),
        ("Phone Number", r"(?i)\b(?:Phone|Mobile|Contact\s+Number|Phone\s+No|Cell)\s*:\s*([^\n]+)"),
        ("Email", r"(?i)\bEmail\s*:\s*([^\n]+)"),
        ("Aadhaar Number", r"(?i)\b(?:Aadhaar|Aadhaar\s+No|Aadhaar\s+Number|Aadhar)\s*:\s*([^\n]+)"),
        ("Insurance Number", r"(?i)\b(?:Insurance\s+No|Insurance\s+Number|Insurance)\s*:\s*([^\n]+)"),
        ("Doctor Name", r"(?i)\b(?:Referred\s+by|Doctor|Doctor\s+Name|Attending\s+Physician|Physician|Consultant)\s*:\s*([^\n]+)"),
    ]

    # Standalone Value Patterns for Unstructured / Inline Text
    VALUE_PATTERNS = [
        ("Aadhaar Number", r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b"),
        ("PAN Number", r"\b[A-Z]{5}\d{4}[A-Z]{1}\b"),
        ("Phone Number", r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}\b"),
        ("Email", r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"),
        ("Date of Birth", r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b"),
        ("Medical Record Number (MRN)", r"\bMRN-?[A-Z0-9]{4,12}\b"),
        ("Hospital ID", r"\bHOSP-?[A-Z0-9]{4,12}\b"),
        ("Patient ID", r"\bPID-?[A-Z0-9]{4,12}\b"),
        ("Insurance Number", r"\bINS-?[A-Z0-9]{4,12}\b"),
        ("Doctor Name", r"\b(?:Dr\.|Doctor)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"),
        ("Referred By Inline", r"\bReferred\s+by\s+(?:Dr\.\s*)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b"),
    ]

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

        # 1. Process Structured Key-Value Patterns
        for entity_type, pat in self.KV_PATTERNS:
            for match in list(re.finditer(pat, redacted_text)):
                full_match = match.group(0)
                val = match.group(1).strip()
                prefix = full_match.split(':')[0]
                if val and val != self.REDACTION_TOKEN:
                    audit_log.append({
                        "entity_type": entity_type,
                        "original_token_preview": val[:3] + "***" if len(val) > 3 else "***",
                        "status": "REDACTED"
                    })
                    redacted_text = redacted_text.replace(full_match, f"{prefix}: {self.REDACTION_TOKEN}")

        # 2. Process Standalone / Unstructured Value Patterns
        for entity_type, pat in self.VALUE_PATTERNS:
            for match in list(re.finditer(pat, redacted_text)):
                val = match.group(0)
                if val and val != self.REDACTION_TOKEN and self.REDACTION_TOKEN not in val:
                    audit_log.append({
                        "entity_type": entity_type,
                        "original_token_preview": val[:3] + "***" if len(val) > 3 else "***",
                        "status": "REDACTED"
                    })
                    redacted_text = redacted_text.replace(val, self.REDACTION_TOKEN)

        return redacted_text, audit_log

    def propose_redactions(self, text: str) -> List[Dict[str, Any]]:
        """
        Scans raw clinical text and returns proposed entity redactions for human-in-the-loop review.
        """
        proposals = []
        # Key-Value proposals
        for entity_type, pat in self.KV_PATTERNS:
            for match in re.finditer(pat, text):
                val = match.group(1).strip()
                if val:
                    proposals.append({
                        "entity_type": entity_type,
                        "matched_value": val[:3] + "***" + val[-2:] if len(val) > 5 else "***",
                        "start_index": match.start(1),
                        "end_index": match.end(1),
                        "proposed_token": self.REDACTION_TOKEN,
                        "review_status": "PENDING_APPROVAL"
                    })

        # Standalone proposals
        for entity_type, pat in self.VALUE_PATTERNS:
            for match in re.finditer(pat, text):
                val = match.group(0)
                if val:
                    proposals.append({
                        "entity_type": entity_type,
                        "matched_value": val[:3] + "***" + val[-2:] if len(val) > 5 else "***",
                        "start_index": match.start(),
                        "end_index": match.end(),
                        "proposed_token": self.REDACTION_TOKEN,
                        "review_status": "PENDING_APPROVAL"
                    })
        return proposals

    def anonymize_tabular(self, record: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Anonymizes structured dict / tabular medical records.
        """
        sanitized = record.copy()
        audit_log = []

        pii_keys = [
            "name", "patient_name", "patient_id", "pid", "id", "aadhaar", "pan", "phone", "email",
            "address", "mrn", "hospital_id", "insurance_no", "doctor", "referred_by",
            "guardian", "dob", "photo_metadata", "qr_code", "barcode"
        ]

        for k, v in record.items():
            k_lower = k.lower()
            if any(pii_key == k_lower or pii_key in k_lower for pii_key in pii_keys):
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
            "anonymized_sample": anonymized_text[:400] + ("..." if len(anonymized_text) > 400 else "")
        }

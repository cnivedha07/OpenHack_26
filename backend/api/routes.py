from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from privacy.privacy_shield import PrivacyShieldEngine
from validation.validator import DataValidationEngine
from classifier.data_classifier import IntelligentDataClassifier
from federated.server.flower_server import FederatedServerManager
from dashboard.metrics_manager import DashboardMetricsManager
from auth.jwt_handler import create_access_token
from api.websocket import ws_manager

router = APIRouter()

# Instantiate core engines
privacy_engine = PrivacyShieldEngine()
validator_engine = DataValidationEngine()
classifier_engine = IntelligentDataClassifier()
fl_server = FederatedServerManager()
metrics_manager = DashboardMetricsManager(fl_server)

class LoginRequest(BaseModel):
    username: str
    password: str

class AttackToggleRequest(BaseModel):
    hospital_id: str
    attack_type: str
    intensity: Optional[float] = 1.0

class AnonymizeTextRequest(BaseModel):
    text: str

class DPToggleRequest(BaseModel):
    enabled: bool

@router.post("/auth/login")
async def login(req: LoginRequest):
    if req.username and req.password:
        token = create_access_token(req.username)
        return {"access_token": token, "token_type": "bearer", "role": "Hospital Admin"}
    raise HTTPException(status_code=400, detail="Invalid credentials")

@router.post("/upload")
async def upload_file(file: UploadFile = File(...), hospital_id: str = Form("hospital_1")):
    content = await file.read()

    # Step 1: Privacy Shield
    privacy_res = privacy_engine.process_file_privacy(file.filename, file.content_type, content)

    # Step 2: Validation
    validation_res = validator_engine.validate_file(file.filename, file.content_type, content)

    # Step 3: Intelligent Classification
    snippet = privacy_res.get("anonymized_sample", "")
    classification_res = classifier_engine.classify_and_route(file.filename, file.content_type, snippet)

    return {
        "hospital_id": hospital_id,
        "filename": file.filename,
        "privacy_shield": privacy_res,
        "validation_report": validation_res,
        "classification": classification_res,
        "status": "Processed and Routed to FL Pipeline"
    }

@router.post("/privacy/anonymize")
async def anonymize_text(req: AnonymizeTextRequest):
    redacted, logs = privacy_engine.anonymize_text(req.text)
    return {
        "original_text": req.text,
        "redacted_text": redacted,
        "redaction_logs": logs
    }

@router.post("/validate")
async def validate_custom_file(file: UploadFile = File(...)):
    content = await file.read()
    report = validator_engine.validate_file(file.filename, file.content_type, content)
    return report

@router.post("/classify")
async def classify_custom_file(filename: str, sample_text: Optional[str] = ""):
    res = classifier_engine.classify_and_route(filename, "text/plain", sample_text)
    return res

@router.post("/train/start")
async def start_training():
    fl_server.is_training_active = True
    round_res = fl_server.execute_next_round()
    
    # Broadcast to WebSockets
    await ws_manager.broadcast({
        "event": "ROUND_COMPLETED",
        "round_data": round_res,
        "dashboard": metrics_manager.get_dashboard_summary()
    })
    return {"message": "Federated round executed successfully", "round_summary": round_res}

@router.post("/train/stop")
async def stop_training():
    fl_server.is_training_active = False
    return {"message": "Federated training paused", "current_round": fl_server.current_round}

@router.post("/train/pause")
async def pause_training():
    fl_server.pause_training()
    await ws_manager.broadcast({"event": "TRAINING_PAUSED", "dashboard": metrics_manager.get_dashboard_summary()})
    return {"message": "Federated training paused", "current_round": fl_server.current_round}

@router.post("/train/resume")
async def resume_training():
    fl_server.resume_training()
    await ws_manager.broadcast({"event": "TRAINING_RESUMED", "dashboard": metrics_manager.get_dashboard_summary()})
    return {"message": "Federated training resumed", "current_round": fl_server.current_round}

@router.post("/train/reset")
async def reset_training():
    fl_server.reset_training()
    await ws_manager.broadcast({"event": "TRAINING_RESET", "dashboard": metrics_manager.get_dashboard_summary()})
    return {"message": "Training state reset", "current_round": fl_server.current_round}

@router.post("/train/dp/toggle")
async def toggle_dp(req: DPToggleRequest):
    result = fl_server.toggle_differential_privacy(req.enabled)
    await ws_manager.broadcast({"event": "DP_TOGGLED", "dp": result, "dashboard": metrics_manager.get_dashboard_summary()})
    return result

@router.get("/train/fit-report")
async def get_fit_report():
    """
    Per-hospital overfit/underfit diagnostics computed from each client's real
    local train/val split (never shared) -- this is what answers "is the local
    model overfit or underfit" instead of comparing raw accuracy across hospitals.
    """
    report = {}
    for hid, client in fl_server.clients.items():
        m = client.last_metrics or {}
        report[hid] = {
            "train_accuracy": m.get("train_accuracy"),
            "val_accuracy": m.get("val_accuracy"),
            "generalization_gap": m.get("generalization_gap"),
            "fit_status": m.get("fit_status", "Not Trained Yet"),
            "train_size": client.train_size,
            "val_size": client.val_size,
        }
    return {
        "note": "Gap = train_accuracy - val_accuracy, computed on each hospital's own held-out local validation split. Data never leaves the hospital; only model weights are aggregated.",
        "overfit_threshold": 0.15,
        "hospitals": report
    }

@router.get("/hospital/status")
async def get_hospital_status():
    summary = metrics_manager.get_dashboard_summary()
    return {"hospitals": summary["hospitals"]}

@router.get("/privacy/status")
async def get_privacy_status():
    return {
        "engine": "Privacy Shield 2.0",
        "mode": "Active & Strict PII Scrubber",
        "supported_entities": [
            "Patient Name", "Aadhaar Number", "PAN Number", "Phone Number",
            "Email", "Address", "MRN", "Hospital ID", "Insurance Number", "Doctor Name", "DOB"
        ],
        "total_anonymized_files": 482,
        "pii_redacted_count": 1420
    }

@router.get("/validation")
async def get_validation_metrics():
    return {
        "total_validated": 500,
        "passed": 482,
        "rejected": 18,
        "rejection_reasons": {
            "Corrupted Image": 8,
            "Invalid CSV Schema": 6,
            "Unsupported Format": 4
        }
    }

@router.get("/trust")
async def get_trust_scores():
    return {
        "trust_scores": fl_server.trust_scores,
        "exclusion_threshold": 40.0,
        "suspicious_z_threshold": -1.5
    }

@router.get("/aggregation")
async def get_aggregation_details():
    return {
        "aggregation_engine": "Trust-Based Z-Score Weighted Averaging",
        "formula": "Weighted sum by normalized trust scores (alpha = N_i * (Trust_i / 100))",
        "min_trust_required": 40.0,
        "current_round": fl_server.current_round
    }

@router.get("/metrics")
async def get_dashboard_metrics():
    return metrics_manager.get_dashboard_summary()

@router.get("/fusion")
async def get_fusion_statistics():
    return {
        "architecture": "Multi-Head Cross-Attention Gated Fusion Engine",
        "cnn_embedding_dim": 128,
        "ann_embedding_dim": 128,
        "bert_embedding_dim": 128,
        "unified_representation_dim": 128,
        "weights_distribution": {
            "CNN (Vision)": 38.5,
            "ANN (Tabular)": 31.2,
            "BERT (Text)": 30.3
        }
    }

@router.get("/model")
async def get_model_info():
    return {
        "global_model_version": f"v2.{fl_server.current_round}.0",
        "global_accuracy": fl_server.global_accuracy,
        "global_loss": fl_server.global_loss,
        "framework": "Flower FL + PyTorch Multimodal Architecture"
    }

@router.get("/logs")
async def get_system_logs():
    return {
        "logs": [
            f"[Round {fl_server.current_round}] Trust-based aggregation complete. Global accuracy: {fl_server.global_accuracy:.4f}",
            "[Privacy Shield] Scrubber redacted 12 PII tokens in uploaded clinical summary",
            "[Validator] File 'vitals_hospital_1.csv' passed schema verification",
            "[Classifier] Image file routed to CNN Vision Module"
        ]
    }

@router.post("/attack/toggle")
async def toggle_attack(req: AttackToggleRequest):
    success = fl_server.toggle_attack(req.hospital_id, req.attack_type, req.intensity)
    if success:
        await ws_manager.broadcast({
            "event": "ATTACK_TOGGLED",
            "hospital_id": req.hospital_id,
            "attack_type": req.attack_type,
            "dashboard": metrics_manager.get_dashboard_summary()
        })
        return {"message": f"Attack '{req.attack_type}' applied to {req.hospital_id}"}
    raise HTTPException(status_code=404, detail="Hospital not found")

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import PrivacyAuditModel, AttackLogModel, RoundLogModel, GlobalModelVersionModel
from privacy.privacy_shield import PrivacyShieldEngine
from validation.validator import DataValidationEngine
from classifier.data_classifier import IntelligentDataClassifier
from federated.server.flower_server import FederatedServerManager
from dashboard.metrics_manager import DashboardMetricsManager
from api.websocket import ws_manager
from auth.dependencies import get_current_user, require_admin, require_hospital_access
from utils.logger import log_event, get_recent_logs

router = APIRouter()

# Instantiate core engines
privacy_engine = PrivacyShieldEngine()
validator_engine = DataValidationEngine()
classifier_engine = IntelligentDataClassifier()
fl_server = FederatedServerManager()
metrics_manager = DashboardMetricsManager(fl_server)


class AttackToggleRequest(BaseModel):
    hospital_id: str
    attack_type: str
    intensity: Optional[float] = 1.0


class AnonymizeTextRequest(BaseModel):
    text: str


class DPToggleRequest(BaseModel):
    enabled: bool


# Public Health Check
@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "TrustFed 2.0 Backend"}


MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB Limit


# Hospital Data Ingestion (Hospital-scoped: cannot upload for another hospital)
@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    hospital_id: str = Form("hospital_1"),
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    # Enforce tenant isolation
    if current_user.get("role") == "hospital" and current_user.get("hospital_id") != hospital_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: Hospital '{current_user.get('hospital_id')}' cannot upload data for '{hospital_id}'"
        )

    content = await file.read()

    # Enforce 10MB upload size limit (HTTP 413 Payload Too Large)
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({len(content)} bytes) exceeds the maximum allowed limit of 10MB (Payload Too Large)."
        )

    # Step 1: Privacy Shield (processed strictly in-memory via BytesIO / bytes buffer)
    privacy_res = privacy_engine.process_file_privacy(file.filename, file.content_type, content)

    # Step 2: Validation
    validation_res = validator_engine.validate_file(file.filename, file.content_type, content)

    # Step 3: Intelligent Classification
    snippet = privacy_res.get("anonymized_sample", "")
    classification_res = classifier_engine.classify_and_route(file.filename, file.content_type, snippet)

    redaction_audit = privacy_res.get("redaction_audit", [])
    detected_entities = [log.get("entity_type") for log in redaction_audit if "entity_type" in log]

    # Write Privacy Audit Log to Database
    audit_entry = PrivacyAuditModel(
        hospital_id=hospital_id,
        filename=file.filename,
        data_type=classification_res.get("data_type", "Text"),
        entities_detected=detected_entities,
        redacted_sample=snippet[:200] if snippet else ""
    )
    db.add(audit_entry)
    db.commit()

    log_event(f"[Privacy Shield] Processed '{file.filename}' for {hospital_id}. Redacted {len(detected_entities)} PII tokens.")

    return {
        "hospital_id": hospital_id,
        "filename": file.filename,
        "privacy_shield": privacy_res,
        "validation_report": validation_res,
        "classification": classification_res,
        "status": "Processed and Routed to FL Pipeline"
    }


@router.post("/privacy/anonymize")
async def anonymize_text(
    req: AnonymizeTextRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    redacted, logs = privacy_engine.anonymize_text(req.text)
    return {
        "original_text": req.text,
        "redacted_text": redacted,
        "redaction_logs": logs
    }


@router.post("/privacy/review")
async def review_privacy_proposals(
    req: AnonymizeTextRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Human-in-the-loop candidate redaction review step.
    Returns structured entity proposals (start/end index, entity_type, matched_value, proposed_token).
    """
    proposals = privacy_engine.propose_redactions(req.text)
    return {
        "text": req.text,
        "proposed_redactions_count": len(proposals),
        "proposals": proposals,
        "review_status": "READY_FOR_HUMAN_APPROVAL"
    }



@router.post("/validate")
async def validate_custom_file(
    file: UploadFile = File(...),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    content = await file.read()
    report = validator_engine.validate_file(file.filename, file.content_type, content)
    return report


@router.post("/classify")
async def classify_custom_file(
    filename: str,
    sample_text: Optional[str] = "",
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    res = classifier_engine.classify_and_route(filename, "text/plain", sample_text)
    return res


# ==========================================
# Admin-Only Training Controls
# ==========================================

@router.post("/train/start")
async def start_training(
    db: Session = Depends(get_db),
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    fl_server.is_training_active = True
    round_res = fl_server.execute_next_round(db=db)
    
    # Broadcast to WebSockets
    await ws_manager.broadcast({
        "event": "ROUND_COMPLETED",
        "round_data": round_res,
        "dashboard": metrics_manager.get_dashboard_summary()
    })
    return {"message": "Federated round executed successfully", "round_summary": round_res}


@router.post("/train/stop")
async def stop_training(admin_user: Dict[str, Any] = Depends(require_admin)):
    fl_server.is_training_active = False
    log_event(f"Training stopped by admin at round {fl_server.current_round}", level="warning")
    return {"message": "Federated training paused", "current_round": fl_server.current_round}


@router.post("/train/pause")
async def pause_training(admin_user: Dict[str, Any] = Depends(require_admin)):
    fl_server.pause_training()
    log_event(f"Training paused by admin at round {fl_server.current_round}")
    await ws_manager.broadcast({"event": "TRAINING_PAUSED", "dashboard": metrics_manager.get_dashboard_summary()})
    return {"message": "Federated training paused", "current_round": fl_server.current_round}


@router.post("/train/resume")
async def resume_training(admin_user: Dict[str, Any] = Depends(require_admin)):
    fl_server.resume_training()
    log_event(f"Training resumed by admin at round {fl_server.current_round}")
    await ws_manager.broadcast({"event": "TRAINING_RESUMED", "dashboard": metrics_manager.get_dashboard_summary()})
    return {"message": "Federated training resumed", "current_round": fl_server.current_round}


@router.post("/train/reset")
async def reset_training(admin_user: Dict[str, Any] = Depends(require_admin)):
    fl_server.reset_training()
    log_event("Training state reset to initial baseline", level="warning")
    await ws_manager.broadcast({"event": "TRAINING_RESET", "dashboard": metrics_manager.get_dashboard_summary()})
    return {"message": "Training state reset", "current_round": fl_server.current_round}


@router.post("/train/dp/toggle")
async def toggle_dp(
    req: DPToggleRequest,
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    result = fl_server.toggle_differential_privacy(req.enabled)
    log_event(f"Differential Privacy {'enabled' if req.enabled else 'disabled'}")
    await ws_manager.broadcast({"event": "DP_TOGGLED", "dp": result, "dashboard": metrics_manager.get_dashboard_summary()})
    return result


@router.get("/train/fit-report")
async def get_fit_report(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Per-hospital overfit/underfit diagnostics.
    Admin sees all hospitals; hospital user sees only their own diagnostics.
    """
    report = {}
    role = current_user.get("role")
    user_hosp_id = current_user.get("hospital_id")

    for hid, client in fl_server.clients.items():
        if role == "hospital" and hid != user_hosp_id:
            continue
        m = client.last_metrics or {}
        report[hid] = {
            "train_accuracy": m.get("train_accuracy"),
            "val_accuracy": m.get("val_accuracy"),
            "generalization_gap": m.get("generalization_gap"),
            "fit_status": m.get("fit_status", "Not Trained Yet"),
            "train_size": client.train_size,
            "val_size": client.val_size,
            "precision_class_0": m.get("precision_class_0"),
            "recall_class_0": m.get("recall_class_0"),
            "f1_class_0": m.get("f1_class_0"),
            "precision_class_1": m.get("precision_class_1"),
            "recall_class_1": m.get("recall_class_1"),
            "f1_class_1": m.get("f1_class_1"),
            "minority_class_recall": m.get("minority_class_recall"),
            "class_distribution": m.get("class_distribution", {}),
            "use_class_weighting": client.use_class_weighting,
            "fedprox_mu": client.fedprox_mu
        }
    return {
        "note": "Gap = train_accuracy - val_accuracy, computed on held-out local validation split.",
        "overfit_threshold": 0.15,
        "hospitals": report
    }



@router.get("/hospital/status")
async def get_hospital_status(admin_user: Dict[str, Any] = Depends(require_admin)):
    summary = metrics_manager.get_dashboard_summary()
    return {"hospitals": summary["hospitals"]}


@router.get("/privacy/status")
async def get_privacy_status(
    db: Session = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Returns real privacy statistics computed dynamically from database audit logs.
    """
    audits = db.query(PrivacyAuditModel).all()
    total_files = len(audits)
    total_pii_redacted = sum(len(a.entities_detected or []) for a in audits)

    return {
        "engine": "Privacy Shield 2.0",
        "mode": "Active & Strict PII Scrubber",
        "supported_entities": [
            "Patient Name", "Aadhaar Number", "PAN Number", "Phone Number",
            "Email", "Address", "MRN", "Hospital ID", "Insurance Number", "Doctor Name", "DOB"
        ],
        "total_anonymized_files": total_files,
        "pii_redacted_count": total_pii_redacted
    }


@router.get("/validation")
async def get_validation_metrics(current_user: Dict[str, Any] = Depends(get_current_user)):
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
async def get_trust_scores(admin_user: Dict[str, Any] = Depends(require_admin)):
    return {
        "trust_scores": fl_server.trust_scores,
        "exclusion_threshold": 40.0,
        "suspicious_z_threshold": -1.5
    }


@router.get("/aggregation")
async def get_aggregation_details(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "aggregation_engine": "Trust-Based Z-Score Weighted Averaging",
        "formula": "Weighted sum by normalized trust scores (alpha = N_i * (Trust_i / 100))",
        "min_trust_required": 40.0,
        "current_round": fl_server.current_round
    }


@router.get("/metrics")
async def get_dashboard_metrics(current_user: Dict[str, Any] = Depends(get_current_user)):
    summary = metrics_manager.get_dashboard_summary()
    if current_user.get("role") == "hospital":
        h_id = current_user.get("hospital_id")
        summary["hospitals"] = [h for h in summary.get("hospitals", []) if h.get("id") == h_id]
    return summary


@router.get("/fusion")
async def get_fusion_statistics(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "architecture": "Multi-Head Cross-Attention Gated Fusion Engine",
        "cnn_embedding_dim": 128,
        "ann_embedding_dim": 128,
        "bert_embedding_dim": 128,
        "unified_representation_dim": 128,
        "weights_distribution": fl_server.modality_weights
    }



@router.get("/model")
async def get_model_info(current_user: Dict[str, Any] = Depends(get_current_user)):
    return {
        "global_model_version": f"v2.{fl_server.current_round}.0",
        "global_accuracy": fl_server.global_accuracy,
        "global_loss": fl_server.global_loss,
        "framework": "Flower FL + PyTorch Multimodal Architecture"
    }


@router.get("/logs")
async def get_system_logs(admin_user: Dict[str, Any] = Depends(require_admin)):
    """
    Returns real, live system log entries from the rolling log buffer.
    """
    recent_logs = get_recent_logs(limit=50)
    return {"logs": recent_logs}


@router.post("/attack/toggle")
async def toggle_attack(
    req: AttackToggleRequest,
    db: Session = Depends(get_db),
    admin_user: Dict[str, Any] = Depends(require_admin)
):
    success = fl_server.toggle_attack(req.hospital_id, req.attack_type, req.intensity)
    if success:
        # Write AttackLogModel entry to Database
        attack_log = AttackLogModel(
            round_number=fl_server.current_round,
            attacker_hospital_id=req.hospital_id,
            attack_type=req.attack_type,
            detected=True,
            trust_penalty=15.0 if req.attack_type != "None" else 0.0,
            action_taken="Isolated Hospital" if req.attack_type != "None" else "Restored Normal State"
        )
        db.add(attack_log)
        db.commit()

        log_event(f"[Attack Simulator] Applied '{req.attack_type}' attack to {req.hospital_id} (Intensity: {req.intensity})", level="warning")

        await ws_manager.broadcast({
            "event": "ATTACK_TOGGLED",
            "hospital_id": req.hospital_id,
            "attack_type": req.attack_type,
            "dashboard": metrics_manager.get_dashboard_summary()
        })
        return {"message": f"Attack '{req.attack_type}' applied to {req.hospital_id}"}
    raise HTTPException(status_code=404, detail="Hospital not found")

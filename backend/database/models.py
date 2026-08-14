from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class HospitalModel(Base):
    __tablename__ = "hospitals"

    id = Column(String, primary_key=True)  # e.g., "hospital_1"
    name = Column(String, nullable=False)   # e.g., "Metro General Hospital"
    status = Column(String, default="Active") # Active, Suspicious, Excluded, Training
    trust_score = Column(Float, default=100.0)
    samples_count = Column(Integer, default=0)
    privacy_shield_active = Column(Boolean, default=True)
    validation_status = Column(String, default="Passed")
    joined_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)


class RoundLogModel(Base):
    __tablename__ = "round_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_number = Column(Integer, nullable=False)
    hospital_id = Column(String, ForeignKey("hospitals.id"))
    trust_score_before = Column(Float)
    trust_score_after = Column(Float)
    z_score = Column(Float)
    cosine_similarity = Column(Float)
    euclidean_distance = Column(Float)
    gradient_norm = Column(Float)
    local_loss = Column(Float)
    local_accuracy = Column(Float)
    is_suspicious = Column(Boolean, default=False)
    status_note = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)


class GlobalModelVersionModel(Base):
    __tablename__ = "global_model_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String, nullable=False)
    round_number = Column(Integer, nullable=False)
    global_accuracy = Column(Float, nullable=False)
    global_loss = Column(Float, nullable=False)
    participating_hospitals = Column(JSON) # List of hospital IDs
    trust_weighted_agg = Column(Boolean, default=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class PrivacyAuditModel(Base):
    __tablename__ = "privacy_audits"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(String, nullable=False)
    filename = Column(String, nullable=False)
    data_type = Column(String, nullable=False) # Image, Text, Tabular
    entities_detected = Column(JSON) # List of detected entity types (e.g. Aadhaar, Name)
    redacted_sample = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


class AttackLogModel(Base):
    __tablename__ = "attack_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_number = Column(Integer, nullable=False)
    attacker_hospital_id = Column(String, nullable=False)
    attack_type = Column(String, nullable=False)
    detected = Column(Boolean, default=True)
    trust_penalty = Column(Float, default=15.0)
    action_taken = Column(String, default="Isolated Hospital")
    timestamp = Column(DateTime, default=datetime.utcnow)


class HospitalAccountModel(Base):
    __tablename__ = "hospital_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    hospital_id = Column(String, ForeignKey("hospitals.id"), nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="hospital", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class AdminAccountModel(Base):
    __tablename__ = "admin_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="admin", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


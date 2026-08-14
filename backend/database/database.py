from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from database.models import Base
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "trustfed.db")
DEFAULT_SQLITE_URL = f"sqlite:///{DB_PATH}"

raw_db_url = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)
if raw_db_url.startswith("postgres://"):
    raw_db_url = raw_db_url.replace("postgres://", "postgresql://", 1)

SQLALCHEMY_DATABASE_URL = raw_db_url

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()
    try:
        from database.models import HospitalModel, HospitalAccountModel, AdminAccountModel
        from auth.jwt_handler import hash_password

        # Seed default hospitals if empty
        if db.query(HospitalModel).count() == 0:
            default_hospitals = [
                HospitalModel(id="hospital_1", name="Metro General Hospital", status="Active", trust_score=98.5, samples_count=200),
                HospitalModel(id="hospital_2", name="St. Jude Research Medical", status="Active", trust_score=96.2, samples_count=180),
                HospitalModel(id="hospital_3", name="Apollo Healthcare Center", status="Active", trust_score=94.1, samples_count=150),
                HospitalModel(id="hospital_4", name="City Care Clinic", status="Active", trust_score=91.8, samples_count=120),
            ]
            db.add_all(default_hospitals)
            db.commit()

        # Seed default admin account if empty
        if db.query(AdminAccountModel).filter_by(username="admin").first() is None:
            admin_account = AdminAccountModel(
                username="admin",
                hashed_password=hash_password("admin123"),
                role="admin"
            )
            db.add(admin_account)

        # Seed default hospital accounts if empty
        for i in range(1, 5):
            h_id = f"hospital_{i}"
            u_name = f"hospital_{i}_user"
            if db.query(HospitalAccountModel).filter_by(username=u_name).first() is None:
                h_account = HospitalAccountModel(
                    hospital_id=h_id,
                    username=u_name,
                    hashed_password=hash_password("hospital123"),
                    role="hospital"
                )
                db.add(h_account)

        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


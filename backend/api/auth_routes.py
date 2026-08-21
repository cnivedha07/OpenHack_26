from datetime import datetime, timezone

from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database.database import get_db
from database.models import AdminAccountModel, HospitalAccountModel
from auth.jwt_handler import create_access_token, verify_password
from auth.dependencies import get_current_user

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    hospital_id: Optional[str] = None
    username: str


@auth_router.post("/admin/login", response_model=AuthTokenResponse)
def admin_login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates platform administrator accounts.
    Returns an admin-scoped JWT with role='admin' and hospital_id=null.
    """
    admin = db.query(AdminAccountModel).filter(AdminAccountModel.username == req.username).first()
    if not admin or not verify_password(req.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials"
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is disabled"
        )

    admin.last_login = datetime.now(timezone.utc)

    db.commit()

    token = create_access_token(user_id=admin.username, role="admin", hospital_id=None)
    return AuthTokenResponse(
        access_token=token,
        role="admin",
        hospital_id=None,
        username=admin.username
    )


@auth_router.post("/hospital/login", response_model=AuthTokenResponse)
def hospital_login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates hospital tenant accounts.
    Returns a hospital-scoped JWT carrying role='hospital' and tenant hospital_id.
    """
    hospital_user = db.query(HospitalAccountModel).filter(HospitalAccountModel.username == req.username).first()
    if not hospital_user or not verify_password(req.password, hospital_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid hospital user credentials"
        )
    if not hospital_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Hospital account is disabled"
        )

    hospital_user.last_login = datetime.now(timezone.utc)

    db.commit()

    token = create_access_token(
        user_id=hospital_user.username,
        role="hospital",
        hospital_id=hospital_user.hospital_id
    )
    return AuthTokenResponse(
        access_token=token,
        role="hospital",
        hospital_id=hospital_user.hospital_id,
        username=hospital_user.username
    )


@auth_router.post("/login", response_model=AuthTokenResponse)
def unified_login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Unified login endpoint supporting both admin and hospital logins.
    Auto-detects account role and issues tenant-scoped JWT.
    """
    # Try admin first
    admin = db.query(AdminAccountModel).filter(AdminAccountModel.username == req.username).first()
    if admin and verify_password(req.password, admin.hashed_password):
        admin.last_login = datetime.now(timezone.utc)

        db.commit()
        token = create_access_token(user_id=admin.username, role="admin", hospital_id=None)
        return AuthTokenResponse(
            access_token=token,
            role="admin",
            hospital_id=None,
            username=admin.username
        )

    # Try hospital account
    hospital_user = db.query(HospitalAccountModel).filter(HospitalAccountModel.username == req.username).first()
    if hospital_user and verify_password(req.password, hospital_user.hashed_password):
        hospital_user.last_login = datetime.now(timezone.utc)

        db.commit()
        token = create_access_token(
            user_id=hospital_user.username,
            role="hospital",
            hospital_id=hospital_user.hospital_id
        )
        return AuthTokenResponse(
            access_token=token,
            role="hospital",
            hospital_id=hospital_user.hospital_id,
            username=hospital_user.username
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password"
    )


@auth_router.get("/me")
def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """
    Returns authenticated user session details from JWT claims.
    """
    return {
        "username": current_user.get("sub"),
        "role": current_user.get("role"),
        "hospital_id": current_user.get("hospital_id"),
        "exp": current_user.get("exp")
    }

import os
import time
import logging
import bcrypt
from typing import Dict, Any, Optional
from jose import jwt, JWTError

logger = logging.getLogger("trustfed.auth")


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "TRUSTFED_DEVELOPMENT_SECRET_KEY_DEV_ONLY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 86400

if SECRET_KEY == "TRUSTFED_DEVELOPMENT_SECRET_KEY_DEV_ONLY":
    logger.warning("Using default development JWT_SECRET_KEY. Set JWT_SECRET_KEY env variable in production.")


def hash_password(password: str) -> str:
    """Hashes a raw password using bcrypt."""
    pwd_bytes = password.encode('utf-8')[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a bcrypt hash."""
    try:
        pwd_bytes = plain_password.encode('utf-8')[:72]
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False



def create_access_token(
    user_id: str,
    role: str = "hospital",
    hospital_id: Optional[str] = None
) -> str:
    """
    Creates a tenant-scoped JWT token.
    Admin tokens carry role='admin' and hospital_id=None.
    Hospital tokens carry role='hospital' and hospital_id='hospital_1' (or similar).
    """
    now = time.time()
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "role": role,
        "hospital_id": hospital_id,
        "iat": int(now),
        "exp": int(now + ACCESS_TOKEN_EXPIRE_SECONDS)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token.
    Returns the payload dictionary if valid, or an empty dictionary if invalid/expired.
    """
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        exp = decoded_token.get("exp")
        if exp and exp >= time.time():
            return decoded_token
        return {}
    except JWTError:
        return {}
    except Exception as e:
        logger.error(f"Error decoding JWT token: {e}")
        return {}


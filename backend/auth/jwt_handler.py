import time
from typing import Dict
from jose import jwt

SECRET_KEY = "TRUSTFED_ENTERPRISE_SECRET_KEY_HEALTHCARE_AI"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 86400

def create_access_token(user_id: str, role: str = "Hospital Admin") -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "expires": time.time() + ACCESS_TOKEN_EXPIRE_SECONDS
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str) -> Dict[str, str]:
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if decoded_token["expires"] >= time.time():
            return decoded_token
        return {}
    except Exception:
        return {}

from typing import Dict, Any, Optional
from fastapi import Depends, HTTPException, Security, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from auth.jwt_handler import verify_token

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Dict[str, Any]:
    """
    Validates Bearer token and returns the current user token claims.
    Raises 401 if missing, invalid, or expired.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload


async def require_admin(
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Enforces that the authenticated user has the 'admin' role.
    Raises 403 Forbidden if the user is not an admin.
    """
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this operation"
        )
    return user


async def require_hospital_access(
    hospital_id: str,
    user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Enforces multi-tenant isolation.
    Hospital users can only access endpoints matching their own hospital_id.
    Admin users are allowed to access any hospital endpoint.
    Raises 403 Forbidden if a hospital user attempts to access another hospital's resource.
    """
    role = user.get("role")
    user_hosp_id = user.get("hospital_id")

    if role == "admin":
        return user

    if role == "hospital":
        if user_hosp_id != hospital_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: Hospital '{user_hosp_id}' cannot access resources belonging to '{hospital_id}'"
            )
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Unauthorized role"
    )

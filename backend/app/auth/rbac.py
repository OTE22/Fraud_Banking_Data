from app.auth.jwt_handler import decode_access_token
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)

ROLE_HIERARCHY: dict[str, list[str]] = {
    "admin": ["admin", "fraud_analyst", "data_scientist", "ml_engineer", "auditor", "soc_team"],
    "fraud_analyst": ["fraud_analyst"],
    "data_scientist": ["data_scientist"],
    "ml_engineer": ["ml_engineer"],
    "auditor": ["auditor"],
    "soc_team": ["soc_team"],
}


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict | None:
    if token is None:
        return None
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return payload


def require_role(required: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        user_roles = user.get("roles", [])
        for r in user_roles:
            if required in ROLE_HIERARCHY.get(r, [r]):
                return user
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
    return checker

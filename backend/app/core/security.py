from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt_handler import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_optional_user(token: str = None) -> dict | None:
    if not token:
        return None
    return decode_access_token(token)

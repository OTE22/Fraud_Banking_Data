from fastapi import Request, HTTPException, Depends
from app.config import get_settings, Settings


def verify_origin(request: Request, settings: Settings = Depends(get_settings)) -> None:
    origin = request.headers.get("origin", "")
    allowed = settings.cors_origins.split(",")
    if origin and origin not in allowed and not settings.debug:
        raise HTTPException(status_code=403, detail="Origin not allowed")

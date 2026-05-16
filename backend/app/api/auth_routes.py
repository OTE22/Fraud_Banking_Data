from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user_schema import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.core.db import get_db
from app.users.services import register_user, authenticate_user
from app.auth.rbac import require_role
from app.core.logging import LOGGER

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(db, body.username, body.email, body.password, body.roles)
        LOGGER.info("user_registered", username=body.username, roles=body.roles)
        return UserResponse(id=user.id, username=user.username, email=user.email, roles=user.roles.split(","), is_active=user.is_active)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await authenticate_user(db, body.username, body.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user, token = result
    LOGGER.info("user_login", username=body.username)
    return TokenResponse(access_token=token, user=UserResponse(id=user.id, username=user.username, email=user.email, roles=user.roles.split(","), is_active=user.is_active))


@router.get("/me", response_model=UserResponse)
async def me(db: AsyncSession = Depends(get_db), user: dict = Depends(require_role("fraud_analyst"))):
    from app.users.repository import get_user_by_id
    uid = user.get("user_id")
    if not uid:
        raise HTTPException(status_code=401, detail="Invalid token")
    u = await get_user_by_id(db, uid)
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=u.id, username=u.username, email=u.email, roles=u.roles.split(","), is_active=u.is_active)

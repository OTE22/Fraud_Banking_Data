from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.user_schema import LoginRequest, TokenResponse, UserCreate, UserResponse
from app.core.db import get_db
from app.users.services import register_user, authenticate_user
from app.auth.rbac import require_role

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse)
async def register(body: UserCreate, db: AsyncSession = Depends(get_db), _=Depends(require_role("admin"))):
    try:
        user = await register_user(db, body.username, body.email, body.password, body.roles)
        return UserResponse(id=user.id, username=user.username, email=user.email, roles=user.roles.split(","), is_active=user.is_active)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await authenticate_user(db, body.username, body.password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    user, token = result
    return TokenResponse(access_token=token, user=UserResponse(id=user.id, username=user.username, email=user.email, roles=user.roles.split(","), is_active=user.is_active))

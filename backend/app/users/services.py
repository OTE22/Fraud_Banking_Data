from sqlalchemy.ext.asyncio import AsyncSession
from app.users.repository import create_user, get_user_by_username, get_user_by_id, list_users, update_user
from app.users.models import UserModel
from app.auth.password_utils import verify_password
from app.auth.jwt_handler import create_access_token


async def register_user(db: AsyncSession, username: str, email: str, password: str, roles: list[str]) -> UserModel:
    existing = await get_user_by_username(db, username)
    if existing:
        raise ValueError("Username already exists")
    existing_email = await get_user_by_username(db, email)
    return await create_user(db, username, email, password, roles)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> tuple[UserModel, str] | None:
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    token = create_access_token({"sub": user.username, "roles": user.roles.split(","), "user_id": user.id})
    return user, token


async def get_user_profile(db: AsyncSession, user_id: int) -> UserModel | None:
    return await get_user_by_id(db, user_id)


async def list_all_users(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[UserModel]:
    return await list_users(db, skip, limit)


async def update_user_roles(db: AsyncSession, user_id: int, roles: list[str]) -> UserModel | None:
    return await update_user(db, user_id, {"roles": ",".join(roles)})

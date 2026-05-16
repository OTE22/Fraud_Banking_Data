from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.users.models import UserModel
from app.auth.password_utils import hash_password


async def create_user(db: AsyncSession, username: str, email: str, password: str, roles: list[str]) -> UserModel:
    user = UserModel(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        roles=",".join(roles),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_username(db: AsyncSession, username: str) -> UserModel | None:
    result = await db.execute(select(UserModel).where(UserModel.username == username))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserModel | None:
    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 50) -> list[UserModel]:
    result = await db.execute(select(UserModel).offset(skip).limit(limit))
    return list(result.scalars())


async def update_user(db: AsyncSession, user_id: int, updates: dict) -> UserModel | None:
    user = await get_user_by_id(db, user_id)
    if not user:
        return None
    for k, v in updates.items():
        if v is not None:
            setattr(user, k, v)
    await db.commit()
    await db.refresh(user)
    return user

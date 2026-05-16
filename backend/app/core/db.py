from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import get_settings
from app.core.logging import LOGGER


def _engine():
    settings = get_settings()
    return create_async_engine(settings.database_url, echo=settings.debug)


engine = _engine()
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    from app.domain.models import Base, PredictionModel
    from app.users.models import UserModel
    from app.auth.password_utils import hash_password
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS detail_json TEXT"))
    async with async_session() as session:
        existing = await session.execute(text("SELECT id FROM users WHERE username='admin'"))
        if not existing.scalar_one_or_none():
            async with engine.begin() as conn:
                await conn.execute(text(
                    "INSERT INTO users (username, email, hashed_password, roles, is_active) VALUES "
                    "('admin', 'admin@bank.com', :pw, 'admin,analyst', true)"
                ), {"pw": hash_password("admin123")})
    LOGGER.info("database_tables_initialized")

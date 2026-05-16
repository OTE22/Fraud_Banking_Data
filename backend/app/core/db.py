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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE predictions ADD COLUMN IF NOT EXISTS detail_json TEXT"))
    LOGGER.info("database_tables_initialized")

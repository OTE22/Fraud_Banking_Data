from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.core.logging import setup_logging, LOGGER
from app.core.db import init_db
from app.core.middleware import RequestLoggingMiddleware
from app.api.routes import router
from app.api.auth_routes import router as auth_router
from app.api.fraud_routes import router as fraud_router
from app.api.drift_routes import router as drift_router
from app.api.admin_routes import router as admin_router
from app.api.segments_routes import router as segments_router
from app.ml.drift import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    LOGGER.info("app_starting", name=get_settings().app_name)
    await init_db()
    start_scheduler()
    yield
    LOGGER.info("app_shutting_down")


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(","), allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.add_middleware(RequestLoggingMiddleware)

app.include_router(router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(fraud_router, prefix="/api/v1")
app.include_router(drift_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(segments_router, prefix="/api/v1")

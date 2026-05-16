from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Enterprise Banking Fraud Detection API"
    debug: bool = False
    model_path: str = "backend/models/fraud_model.pkl"
    anomaly_model_path: str = "backend/models/anomaly_model.pkl"
    segmentation_model_path: str = "backend/models/segmentation_model.pkl"
    feast_repo_path: str = "backend/feature_repo"
    drift_interval_hours: int = 6
    drift_threshold: float = 0.15
    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fraud_detection"
    api_port: int = 8000
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:8080"
    secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    kafka_bootstrap_servers: str = "localhost:9092"
    prometheus_enabled: bool = False
    role_hierarchy: dict = {
        "admin": ["admin", "fraud_analyst", "data_scientist", "ml_engineer", "auditor", "soc_team"],
        "fraud_analyst": ["fraud_analyst"],
        "data_scientist": ["data_scientist"],
        "ml_engineer": ["ml_engineer"],
        "auditor": ["auditor"],
        "soc_team": ["soc_team"],
    }

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()

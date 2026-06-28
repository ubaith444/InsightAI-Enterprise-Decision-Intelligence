from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "InsightAI"
    app_env: str = "local"
    api_prefix: str = "/api/v1"
    secret_key: str = Field(default="change-me-in-production")
    access_token_minutes: int = 60 * 8
    cors_origins: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    database_url: str = "sqlite:///./insightai.db"
    mongo_url: str = "mongodb://localhost:27017"
    mongo_database: str = "insightai"
    redis_url: str = "redis://localhost:6379/0"
    celery_task_always_eager: bool = True
    openai_api_key: str | None = None
    default_query_limit: int = 100
    query_timeout_seconds: int = 15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


def validate_environment() -> dict[str, str]:
    settings = get_settings()
    checks = {
        "SECRET_KEY": "configured" if settings.secret_key != "change-me-in-production" else "default-warning",
        "DATABASE_URL": "configured" if settings.database_url else "missing",
        "MONGO_URL": "configured" if settings.mongo_url else "missing",
        "REDIS_URL": "configured" if settings.redis_url else "missing",
        "OPENAI_API_KEY": "configured" if settings.openai_api_key else "mock-mode",
    }
    return checks

from datetime import timedelta
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict 


# Project base directory
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """
    Global application settings for FastAPI.

    Configuration is loaded from environment variables and `.env` files
    following 12-factor app principles.
    """
    PROJECT_NAME: str = "Hisab NikaX"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", description="development | production | test")

   
    # Security / JWT
    SECRET_KEY: str = Field(default="secretkey")
    JWT_SECRET_KEY: str = Field(default="supersecret")
    JWT_ALGORITHM: str = "HS256"

    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(hours=24)

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: f"sqlite:///{BASE_DIR / 'database' / 'app.db'}"
    )

    # API
    API_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    # Testing
    TESTING: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings instance.
    Ensures settings are loaded only once per process.
    """
    return Settings()


# Single import point
settings = get_settings()

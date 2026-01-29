from datetime import timedelta
from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project base directory
BASE_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """
    Global application settings for FastAPI.

    Configuration is loaded from environment variables and `.env` files
    following 12-factor app principles.
    """

    PROJECT_NAME: str = "Hisab NikaX"
    VERSION: str = "1.0.0"
    SUMMARY: str = "A Unified, Scalable ERP Platform for Smart Business Management"
    DESCRIPTION: str = """**Hisab NikaX** is a comprehensive ERP application designed to streamline 
    and unify core business functions across operations, finance, inventory, sales, and user 
    management. Built with a modular architecture, it provides role-based access control, 
    real-time data tracking, and intuitive dashboards to empower enterprises with actionable 
    insights, increased efficiency, and automated workflows. By integrating robust authentication, 
    secure transaction handling, and scalable database design, Hisab NikaX enables organizations 
    to optimize processes, enhance decision-making, and support growth with a flexible, modern
    backend foundation."""

    CONTACT: dict = {
        "name": "Tapendu Karmakar",
        "url": "https://github.com/iamtapendu",
        "email": "tapendukarma@gmail.com",
    }

    LICENCE: dict = {
        "name": " GNU General Public License v3.0 ",
        "url": "https://www.gnu.org/licenses/gpl-3.0.html#license-text",
    }

    ENVIRONMENT: str = Field(default="development", description="development | production | test")

    # Security / JWT
    SECRET_KEY: str = Field(default="secretkey")
    JWT_SECRET_KEY: str = Field(default="supersecret")
    JWT_ALGORITHM: str = "HS256"

    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(minutes=5)
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(minutes=30)

    # Database
    DATABASE_URL: str = Field(
        default_factory=lambda: f"sqlite:///{BASE_DIR / 'database' / 'app.db'}"
    )

    # API
    API_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://192.168.1.15:5173",
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

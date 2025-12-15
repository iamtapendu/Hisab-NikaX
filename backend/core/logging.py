import logging
import logging.config
from pathlib import Path
from typing import Literal

from .config import settings


LOG_LEVEL = "DEBUG" if settings.ENVIRONMENT == "development" else "INFO"

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def configure_logging() -> None:
    """
    Configure application-wide logging.

    Features:
    - Console logging (development-friendly)
    - Rotating file handlers (production-safe)
    - Separate error log
    - Consistent formatting across app and server
    - Compatible with uvicorn and gunicorn
    """

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,

        # Formatters
        "formatters": {
            "standard": {
                "format": (
                    "%(asctime)s | %(levelname)s | %(name)s | "
                    "%(filename)s:%(lineno)d | %(message)s"
                )
            },
            "access": {
                "format": (
                    "%(asctime)s | ACCESS | %(client_addr)s | "
                    "%(request_line)s | %(status_code)s"
                )
            },
        },

        # Handlers
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": LOG_LEVEL,
            },
            "app_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filename": LOG_DIR / "app.log",
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 10,
                "encoding": "utf-8",
                "level": LOG_LEVEL,
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "standard",
                "filename": LOG_DIR / "error.log",
                "maxBytes": 10 * 1024 * 1024,
                "backupCount": 10,
                "encoding": "utf-8",
                "level": "ERROR",
            },
        },

        # Loggers
        "loggers": {
            # Application logger
            "app": {
                "handlers": ["console", "app_file", "error_file"],
                "level": LOG_LEVEL,
                "propagate": False,
            },

            # SQLAlchemy logging
            "sqlalchemy.engine": {
                "handlers": ["console", "app_file"],
                "level": "WARNING",
                "propagate": False,
            },

            # Uvicorn loggers
            "uvicorn": {
                "handlers": ["console", "app_file"],
                "level": LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console", "error_file"],
                "level": LOG_LEVEL,
                "propagate": False,
            },
            "uvicorn.access": {
                "handlers": ["console", "app_file"],
                "level": "INFO",
                "propagate": False,
            },
        },

        # Root Logger
        "root": {
            "handlers": ["console", "app_file"],
            "level": LOG_LEVEL,
        },
    }

    logging.config.dictConfig(logging_config)

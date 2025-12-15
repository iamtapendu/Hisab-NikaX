from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from core.config import settings

engine = create_engine(settings.DATABASE_URL, future=True)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    FastAPI dependency that provides a SQLAlchemy session.

    Ensures:
    - One session per request
    - Proper cleanup after request completion
    """
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()

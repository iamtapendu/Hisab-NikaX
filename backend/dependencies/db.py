from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from database.session import SessionLocal


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

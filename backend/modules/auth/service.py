from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import delete, select
from fastapi import HTTPException, status

from core.security import (
    TokenType,
    JWTPayload,
    create_access_token,
    create_refresh_token,
    verify_password,
)
from modules.users.model import User
from .model import RevokedToken


def revoke_token(db: Session, payload: JWTPayload) -> None:
    """
    Revoke JWT token using JTI
    """
    db.add(
        RevokedToken(
            jti=payload["jti"],
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    )
    db.commit()


def rotate_refresh_token(db: Session, payload: JWTPayload) -> dict[str, str]:
    """
    Rotate refresh token -
    - Revoke old refresh token
    - Issue new access + refresh tokens
    """
    if payload["type"] != TokenType.refresh:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "msg": "Invalid token type",
                "errors": f"Token Type needed Refresh. Received {payload["type"]}.",
            },
        )

    revoke_token(db=db, payload=payload)

    access_token = create_access_token(
        subject=payload["sub"],
        role=payload["role"],
    )

    refresh_token = create_refresh_token(
        subject=payload["sub"],
        role=payload["role"],
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def cleanup_expired_tokens(db: Session) -> None:
    """
    Cleaned up old expired tokens.
    """
    stmt = delete(RevokedToken).where(RevokedToken.expires_at < datetime.now(timezone.utc))
    db.execute(stmt)
    db.commit()


def authenticate_user(db: Session, username: str, password: str) -> dict[str, str]:
    """
    Authenticate user and generate JWT tokens.

    This validates the provided username and password and returns
    both an access token and a refresh token upon successful login.
    """

    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "msg": "Not able to login.",
                "errors": "Invalid username or password",
            },
        )

    access_token = create_access_token(
        subject=user.id,
        role=user.role,
    )

    refresh_token = create_refresh_token(
        subject=user.id,
        role=user.role,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

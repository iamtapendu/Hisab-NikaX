from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import select

from dependencies.db import get_db
from core.security import TokenType, JWTPayload, oauth2_scheme, decode_token
from modules.users.model import User
from modules.auth.model import RevokedToken


def is_token_revoked(
    jti: str,
    db: Annotated[Session, Depends(get_db)],
) -> bool:
    """
    Docstring for is_token_revoked
    """

    stmt = select(RevokedToken).where(RevokedToken.jti == jti)
    return db.scalar(stmt) is not None


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Retrieve the currently authenticated user from JWT token.
    """
    user_id = decode_token(token, token_type=TokenType.access)["sub"]

    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "msg": "User id not found",
                "errors": None,
            },
        )

    return user


def get_current_refresh_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> JWTPayload:
    """
    Validate and decode refresh token.
    """

    payload = decode_token(token, token_type=TokenType.refresh)

    if is_token_revoked(jti=payload["jti"], db=db):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "msg": "Invalid token",
                "errors": f"Token has been revoked.",
            },
        )

    return payload


def get_current_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> JWTPayload:
    """
    Validate and decode access token.
    """
    payload = decode_token(token, token_type=TokenType.access)
    return payload


def require_roles(*roles: str) -> Callable:
    """
    Dependency factory for role-based access control.

    e.g. Depends(require_roles("admin", "manager"))
    """

    def _require_roles(
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> None:
        payload = decode_token(token, token_type=TokenType.access)

        if payload["role"] not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "msg": "User does not have sufficient permission",
                    "errors": (
                        f"User has '{payload['role']}'. " f"Required one of {', '.join(roles)}."
                    ),
                },
            )

    return _require_roles

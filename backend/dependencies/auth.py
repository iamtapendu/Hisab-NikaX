from typing import Annotated

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

    :param db: Session object
    :type db: Session
    :param jti: JWT token JTI
    :type jti: str
    :return: True/False
    :rtype: bool
    """

    stmt = select(RevokedToken).where(RevokedToken.jti == jti)
    return db.scalar(stmt) is not None


# Get Current Authenticated User
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """
    Retrieve the currently authenticated user from JWT token.

    :param token: JWT access token
    :type token: Annotated[str, Depends(oauth2_scheme)]
    :param db: Session object
    :type db: Annotated[Session, Depends(get_db)]
    :return: User model
    :rtype: User
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


# Role-Based Access Control
async def require_roles(*roles: str):
    """
    Dependency factory for role-based access control.

    :param roles: User roles
    :type roles: str
    """

    def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        """
        Check users roles

        :param current_user: current user
        :type current_user: Annotated[User, Depends(get_current_user)]
        :return: current user
        :rtype: User
        """
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "msg": "User does not have sufficient permission",
                    "errors": f"User have {current_user.role}. Required {", ".join(roles)}.",
                },
            )
        return current_user

    return role_checker


async def get_current_refresh_token(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> JWTPayload:
    """
    Validate and decode refresh token.

    :param token: get current jwt token oauth2 scheme
    :type token: Annotated[str, Depends(oauth2_scheme)]
    :return: decoded JWT token
    :rtype: JWTPayload
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


async def get_current_access_token(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> JWTPayload:
    """
    Validate and decode access token.

    :param token: get current jwt token oauth2 scheme
    :type token: Annotated[str, Depends(oauth2_scheme)]
    :return: decoded JWT token
    :rtype: JWTPayload
    """
    payload = decode_token(token, token_type=TokenType.access)
    return payload

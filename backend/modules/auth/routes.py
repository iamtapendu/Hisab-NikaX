from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import Annotated

from core.security import JWTPayload, OAuth2PasswordRequestFormStrict
from .schema import TokenResponse
from core.common import ErrorResponse
from dependencies.auth import get_current_refresh_token
from dependencies.db import get_db
from modules.auth import service as auth_service

router = APIRouter(tags=["Auth"])


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Authenticate user and generate JWT tokens",
    responses={
        400: {"model": ErrorResponse, "description": "Invalid input"},
        401: {"model": ErrorResponse, "description": "Invalid credential"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def login(
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestFormStrict, Depends()],
):
    """
    Authenticate user and generate JWT tokens.

    This endpoint validates the provided username and password and returns
    both an access token and a refresh token upon successful login.
    """
    return auth_service.authenticate_user(
        db=db,
        username=form_data.username,
        password=form_data.password,
    )


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    response_model=TokenResponse,
    summary="Generate a new access and refresh token.",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid token"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def refresh_token(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[JWTPayload, Depends(get_current_refresh_token)],
):
    """
    Generate a new access token using the refresh token.

    This endpoint is used when an access token has expired. The client
    sends a valid refresh token to obtain a new access token.
    """
    return auth_service.rotate_refresh_token(db=db, payload=token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout by revoking token",
    responses={
        401: {"model": ErrorResponse, "description": "Invalid token"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def logout(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[JWTPayload, Depends(get_current_refresh_token)],
):
    """
    Logout user by refresh token.
    """
    auth_service.revoke_token(db=db, payload=token)
    auth_service.cleanup_expired_tokens(db=db)

from typing import Annotated
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from core.common import ErrorResponse, PaginatedResponse
from dependencies.auth import get_current_user, required_roles
from dependencies.db import get_db
from modules.users import service as user_service
from .model import User
from .schema import UserCreate, UserPasswordUpdate, UserRead, UserUpdate


router = APIRouter(tags=["Users"])


@router.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
    summary="Retrieve current user profile",
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_profile(current_user: Annotated[User, Depends(get_current_user)]):
    """
    Retrieve current user profile

    Fetches a specific user from the database using their unique primary key.
    Typically used for viewing user profiles, pre-filling edit forms, or
    administrative inspection of a particular user record.

    Access Control
    --------------
    - **Anyone**: Can fetch records of their profile
    """
    return current_user


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[UserRead],
    dependencies=[Depends(required_roles("admin"))],
    summary="Retrieve a paginated list of all users.",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_users(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """
    Retrieve a paginated list of all users.

    This endpoint returns user records in paginated form, helping the frontend
    efficiently load users in pages (e.g., 50 per request) instead of fetching
    all records at once.

    Access Control
    --------------
    - **Admin**: Can fetch records of all users
    """
    data, meta = user_service.get_users(db, page, per_page)
    return {
        "data": data,
        "meta": meta,
    }


@router.get(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
    dependencies=[Depends(required_roles("admin"))],
    summary="Retrieve a single user by ID.",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        404: {"model": ErrorResponse, "description": "User not found"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_user(
    db: Annotated[Session, Depends(get_db)],
    user_id: Annotated[int, Path(description="User id", ge=1)],
):
    """
    Retrieve a single user by ID.

    Fetches a specific user from the database using their unique primary key.
    Typically used for viewing user profiles, pre-filling edit forms, or
    administrative inspection of a particular user record.

    Access Control
    --------------
    - **Admin**: Can fetch records of any user by user id
    """
    return user_service.get_user(db, user_id)


@router.get(
    "/username/{username}",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
    dependencies=[Depends(required_roles("admin"))],
    summary="Retrieve a single user by username.",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        404: {"model": ErrorResponse, "description": "User not found"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_user_by_username(
    db: Annotated[Session, Depends(get_db)],
    username: Annotated[str, Path(description="user username", min_length=3, max_length=20)],
):
    """
    Retrieve a single user by useranme.

    Fetches a specific user from the database using their unique username.
    Typically used for viewing user profiles, pre-filling edit forms, or
    administrative inspection of a particular user record.

    Access Control
    --------------
    - **Admin**: Can fetch records of any user by username
    """
    return user_service.get_user_by_username(db, username)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRead,
    dependencies=[Depends(required_roles("admin"))],
    summary="Create new user",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        409: {"model": ErrorResponse, "description": "Username already exists"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def create_user(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[UserCreate, Body(description="new user data")],
):
    """
    Create a new user in the system.

    This endpoint allows administrators to create new users. Only fields that are
    provided and pass regex validation will be assigned; all other fields fall back
    to SQLAlchemy model defaults. Duplicate username checks are performed before
    user creation. Password is always required and stored in a securely hashed form.

    Access Control
    --------------
    - **Admin**: Can create user's profile
    """
    return user_service.create_user(db, payload)


@router.put(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
    summary="Update an existing user's information",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        409: {"model": ErrorResponse, "description": "Username already exists"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def update_user(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: Annotated[int, Path(description="User id", ge=1)],
    payload: Annotated[UserUpdate, Body(description="Updated values")],
):
    """
    Update an existing user's information.

    This endpoint allows users and administrators to update specific user fields such as
    username, email, name, phone, role, image. Only the fields
    included in the incoming JSON payload will be updated. Each field is
    validated against its corresponding regex pattern before being saved.

    Access Control
    --------------
    - **Admin**: Can update any user's profile (including role)
    - **Others**: Can update only their own profile (role changes not allowed)
    """
    # Check for admin user
    if current_user.role == "admin":
        is_admin = True
    else:
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "msg": "Not able to update this user data",
                    "errors": "Admin privileges required",
                },
            )
        is_admin = False

    return user_service.update_user(db, user_id, payload, is_admin)


@router.patch(
    "/{user_id}",
    status_code=status.HTTP_200_OK,
    response_model=UserRead,
    summary="Update an existing user's password",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        409: {"model": ErrorResponse, "description": "Same Password"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def update_password(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: Annotated[int, Path(description="User id", ge=1)],
    payload: Annotated[UserPasswordUpdate, Body(description="old and new password")],
):
    """
    This endpoint allows users to update password.

    This endpoint allows users and administrators to update specific user password.
    Each field is validated against its corresponding regex pattern before being saved.

    Access Control
    --------------
    - **Admin**: Can update any user's password even without current password
    - **Others**: Can update only their own password
    """
    # Check for admin user
    if current_user.role != "admin":
        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "msg": "Not able to update this user password",
                    "errors": "Admin privileges required",
                },
            )

    is_admin = current_user.role == "admin"

    return user_service.update_password(db, user_id, payload, is_admin)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(required_roles("admin"))],
    summary="Delete a user by user id",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def delete_user(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    user_id: Annotated[int, Path(description="User id", ge=1)],
):
    """
    Delete a user by ID.

    This endpoint permanently removes a user record from the database based on
    the provided user ID.

    Access Control
    --------------
    - **Admin**: Can delete any user's profile (excluding own profile)
    """
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "msg": "Not able to delete user",
                "errors": "Admin cannot delete own account",
            },
        )

    user_service.delete_user(db, user_id)

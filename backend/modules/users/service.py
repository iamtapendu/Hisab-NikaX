from typing import Tuple, Sequence
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import HTTPException, status

from core.security import hash_password, verify_password
from core.validators import Pattern, validate_map
from .model import User
from .schema import UserCreate, UserUpdate, UserPasswordUpdate


def get_users(db: Session, page: int, per_page: int) -> Tuple[Sequence[User], dict[str, int]]:
    """
    Service for getting paginated users
    """

    stmt = select(User).order_by(User.last_updated).offset((page - 1) * per_page).limit(per_page)
    users = db.execute(stmt).scalars().all()

    total = db.execute(select(func.count()).select_from(User)).scalar()
    pages = (total + per_page - 1) // per_page if total else 0

    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
    }

    return users, pagination


def get_user(db: Session, user_id: int) -> User:
    """
    Service for fetching one user record using user_id
    """
    user = db.execute(select(User).where(User.id == user_id)).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "msg": "User not found",
                "errors": None,
            },
        )

    return user


def get_user_by_username(db: Session, username: str) -> User:
    """
    Docstring for get_user_by_username
    """
    user = db.execute(select(User).where(User.username == username)).scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "msg": "User not found",
                "errors": None,
            },
        )

    return user


def create_user(db: Session, data: UserCreate) -> User:
    """
    User service for creating users along with extra validation of the fields data.
    """
    # Check username uniqueness
    if db.execute(select(User).where(User.username == data.username)).scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "msg": "Username must be unique",
                "errors": f"Received {data.username} is already exists",
            },
        )

    validate_map(
        data=data,
        validators={
            "username": Pattern.USERNAME_REGX,
            "password": Pattern.PASSWORD_REGX,
            "name": Pattern.NAME_REGX,
            "email": Pattern.EMAIL_REGX,
            "phone": Pattern.PHONE_REGX,
            "role": Pattern.ROLE_REGX,
            "image": Pattern.IMAGE_REGX,
        },
    )

    user = User(
        username=data.username,
        password_hash=hash_password(data.password),
        name=data.name,
        email=data.email,
        phone=data.phone,
        role=data.role,
        image=data.image,
    )

    try:
        db.add(user)
        db.commit()
        db.refresh(user)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Failed to create user",
                "errors": "Database Error: " + str(e),
            },
        )

    return user


def update_user(db: Session, user_id: int, data: UserUpdate, is_admin: bool) -> User:
    """
    Service for updating the user data with some validations
    """
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "User id not found", "errors": None},
        )

    validate_map(
        data=data,
        validators={
            "username": Pattern.USERNAME_REGX,
            "name": Pattern.NAME_REGX,
            "email": Pattern.EMAIL_REGX,
            "phone": Pattern.PHONE_REGX,
            "role": Pattern.ROLE_REGX,
            "image": Pattern.IMAGE_REGX,
        },
    )

    data_dict = data.model_dump(exclude_unset=True)

    if data_dict == {}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": "Nothing to update",
                "errors": f"Empty payload.",
            },
        )

    if data_dict.get("username") and data_dict["username"] != user.username:
        exists = db.execute(
            select(User.id).where(
                User.username == data_dict["username"],
                User.id != user.id,
            )
        ).scalar_one_or_none()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "msg": "Username must be unique",
                    "errors": f"Username '{data_dict["username"]}' already exists",
                },
            )

    if not is_admin:
        data_dict.pop("role", None)

    for field, value in data_dict.items():
        setattr(user, field, value)

    try:
        user.last_updated = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Failed to update user",
                "errors": f"Database error: {str(e)}",
            },
        )

    return user


def update_password(db: Session, user_id: int, data: UserPasswordUpdate, is_admin: bool) -> User:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "User id not found", "errors": None},
        )

    validate_map(data=data, validators={"new_password": Pattern.PASSWORD_REGX})

    if not is_admin:
        if not verify_password(data.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"msg": "Wrong current password", "errors": None},
            )

        if data.current_password == data.new_password:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "msg": "Current and new password must be different",
                    "errors": "Current and new password are same",
                },
            )

    try:
        user.password_hash = hash_password(data.new_password)
        user.last_updated = datetime.now(timezone.utc)
        db.commit()
        db.refresh(user)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Failed to update user's password",
                "errors": f"Database error: {str(e)}",
            },
        )

    return user


def delete_user(db: Session, user_id) -> None:
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "User id not found", "errors": None},
        )

    try:
        db.delete(user)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Failed to delete user",
                "errors": f"Database error: {str(e)}",
            },
        )

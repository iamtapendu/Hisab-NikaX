from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# Base Schema
class UserBase(BaseModel):
    """
    Shared properties for User schemas.
    """

    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9._]+$",
    )
    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[A-Za-z][A-Za-z0-9 ]{3,49}$",
    )
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=10,
        pattern=r"^[6-9]\d{9}$",
    )
    role: str = Field(
        default="guest",
        max_length=10,
        pattern=r"^(admin|manager|staff|guest)$",
    )
    image: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9_/\-]+\.(jpg|jpeg|png)$",
    )


# Create Schema
class UserCreate(UserBase):
    """
    Schema for creating a new user.
    """

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        pattern=r"[A-Za-z\d@$!%*?&#^]{8,}$",
    )


# Update Schema
class UserUpdate(BaseModel):
    """
    Schema for updating an existing user.
    All fields are optional.
    """

    username: str | None = Field(
        default=None,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9._]+$",
    )
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        pattern=r"^[A-Za-z][A-Za-z0-9 ]{1,49}$",
    )
    email: EmailStr | None = None
    phone: str | None = Field(
        default=None,
        min_length=10,
        max_length=10,
        pattern=r"^[6-9]\d{9}$",
    )
    role: str = Field(
        default="guest",
        max_length=10,
        pattern=r"^(admin|manager|staff|guest)$",
    )
    image: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9_/\-]+\.(jpg|jpeg|png)$",
    )


# Password Update Schema
class UserPasswordUpdate(BaseModel):
    """
    Schema for updating user password
    """

    current_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        pattern=r"^[A-Za-z\d@$!%*?&#^]{8,}$",
    )
    new_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        pattern=r"^[A-Za-z\d@$!%*?&#^]{8,}$",
    )


# Read / Response Schema
class UserRead(UserBase):
    """
    Schema returned in API responses.
    """

    id: int
    created_at: datetime
    last_updated: datetime

    class ConfigDict:
        from_attributes = True

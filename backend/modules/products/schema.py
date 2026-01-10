from datetime import datetime

from pydantic import BaseModel, Field


# Base Schema
class ProductBase(BaseModel):
    """
    Shared properties for Product schemas.
    """

    name: str = Field(
        ...,
        min_length=3,
        max_length=256,
    )

    description: str | None = Field(
        default=None,
        min_length=3,
        max_length=256,
    )

    buy_price: float = Field(
        ...,
        ge=0,
        le=99999,
    )

    sell_price: float = Field(
        ...,
        ge=0,
        le=99999,
    )

    mrp: float | None = Field(
        default=None,
        ge=0,
        le=99999,
    )

    hsn_code: str | None = Field(
        default=None,
        min_length=4,
        max_length=8,
        pattern=r"^\d*$",
    )

    gst: float | None = Field(
        default=None,
        ge=0,
        lt=1,
    )

    quantity: int | None = Field(
        default=0,
        ge=0,
        lt=1,
    )

    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
        pattern=r"^(pcs|kg|gram|grs|ltr|ml|box|pkt|set|dozen)$",
    )

    brand: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    model: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    image: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9_/\-]+\.(jpg|jpeg|png)$",
    )


class ProductUpdate(BaseModel):
    """
    Schema for updating an existing user.
    All fields are optional.
    """

    name: str | None = Field(
        default=None,
        min_length=3,
        max_length=256,
    )

    description: str | None = Field(
        default=None,
        min_length=3,
        max_length=256,
    )

    buy_price: float | None = Field(
        default=None,
        ge=0,
        le=99999,
    )

    sell_price: float | None = Field(
        default=None,
        ge=0,
        le=99999,
    )

    mrp: float | None = Field(
        default=None,
        ge=0,
        le=99999,
    )

    hsn_code: str | None = Field(
        default=None,
        min_length=4,
        max_length=8,
        pattern=r"^\d*$",
    )

    gst: float | None = Field(
        default=None,
        ge=0,
        le=40,
    )

    quantity: int | None = Field(
        default=None,
        ge=0,
    )

    unit: str | None = Field(
        default=None,
        min_length=1,
        max_length=20,
        pattern=r"^(pcs|kg|gram|grs|ltr|ml|box|pkt|set|dozen)$",
    )

    brand: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    model: str | None = Field(
        default=None,
        min_length=3,
        max_length=50,
    )

    image: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9_/\-]+\.(jpg|jpeg|png)$",
    )


class ProductRead(ProductBase):
    """
    Schema returned in API responses.
    """

    id: int
    created_at: datetime
    last_updated: datetime

    class ConfigDict:
        from_attributes = True

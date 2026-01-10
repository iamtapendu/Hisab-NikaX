from datetime import datetime, timezone

from sqlalchemy import String, Integer, Float, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from database.base import Base


class Product(Base):
    """
    Product model for the ERP system.

    Represents each item stored in inventory along with pricing,
    tax information, stock levels, and meta-identification details.
    """

    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Basic details
    name = mapped_column(String(256), nullable=False, unique=True)
    description = mapped_column(String(256))

    # Pricing
    buy_price = mapped_column(Float, nullable=False)
    sell_price = mapped_column(Float, nullable=False)
    mrp = mapped_column(Float, nullable=True)

    # GST
    hsn_code = mapped_column(String(10), nullable=True)
    gst = mapped_column(Float, nullable=True)

    # Stock
    quantity = mapped_column(Integer, default=0, nullable=True)

    # Meta
    unit = mapped_column(String(20), default="pcs", nullable=True)
    brand = mapped_column(String(50), nullable=True)
    model = mapped_column(String(50), nullable=True)
    image = mapped_column(String(100), nullable=True)

    created_at = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    last_updated = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

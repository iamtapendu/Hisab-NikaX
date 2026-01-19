from typing import Tuple, Sequence
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import select, func, asc, desc, or_, and_
from fastapi import HTTPException, status

from core.validators import Pattern, validate_map
from .model import Product
from .schema import ProductBase, ProductUpdate


SORTABLE_COLUMNS = {
    "name": Product.name,
    "buy_price": Product.buy_price,
    "sell_price": Product.sell_price,
    "mrp": Product.mrp,
    "quantity": Product.quantity,
    "brand": Product.brand,
    "last_updated": Product.last_updated,
}


def get_products(
    db: Session, page: int, per_page: int, order_by: str, order_dir: str
) -> Tuple[Sequence[Product], dict[str, int]]:
    """
    Service for getting paginated products
    """
    order_by_col = SORTABLE_COLUMNS.get(order_by, Product.last_updated)
    order_stmt = asc(order_by_col) if order_dir == "asc" else desc(order_by_col)

    stmt = select(Product).order_by(order_stmt).offset((page - 1) * per_page).limit(per_page)
    products = db.execute(stmt).scalars().all()

    total = db.execute(select(func.count()).select_from(Product)).scalar()
    pages = (total + per_page - 1) // per_page if total else 0

    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
    }

    return products, pagination


def get_product(db: Session, product_id: int) -> Product:
    """
    Service for getting specific product by id
    """
    product = db.get(Product, product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "msg": "Product not found",
            },
        )

    return product


def search_products(
    db: Session,
    *,
    keywords: str | None,
    page: int = 1,
    per_page: int = 50,
    min_price: float | None = None,
    max_price: float | None = None,
    in_stock: bool | None = None,
    brand: str | None = None,
    unit: str | None = None,
    order_by: str,
    order_dir: str,
) -> Tuple[Sequence[Product], dict[str, int]]:
    """
    Service for searching product using specific keywords
    """
    stmt = select(Product)
    conditions = []

    if keywords:
        words = [word.strip() for word in keywords.split() if word.strip()]

        like = "%" + "%".join(words) + "%"
        conditions.append(
            or_(
                Product.name.ilike(like),
                Product.brand.ilike(like),
                Product.model.ilike(like),
                Product.description.ilike(like),
            )
        )

    if min_price is not None:
        conditions.append(Product.sell_price >= min_price)

    if max_price is not None:
        conditions.append(Product.sell_price <= max_price)

    if in_stock is True:
        conditions.append(Product.quantity > 0)
    elif in_stock is False:
        conditions.append(Product.quantity == 0)

    if brand:
        conditions.append(Product.brand.ilike(f"%{brand}%"))

    if unit:
        conditions.append(Product.unit == unit)

    if conditions:
        stmt = stmt.where(and_(*conditions))

    total = db.execute(
        select(func.count()).select_from(stmt.order_by(None).subquery())
    ).scalar_one()

    order_by_col = SORTABLE_COLUMNS.get(order_by, Product.last_updated)
    order_stmt = asc(order_by_col) if order_dir == "asc" else desc(order_by_col)

    stmt = stmt.order_by(order_stmt).offset((page - 1) * per_page).limit(per_page)
    products = db.execute(stmt).scalars().all()

    pages = (total + per_page - 1) // per_page if total else 0

    meta = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
    }

    return products, meta


def create_product(db: Session, data: ProductBase) -> Product:
    """
    Service for creating products along with extra validation of the fields data.
    """
    if db.execute(select(Product).where(Product.name == data.name)).scalar():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "msg": "Product name must be unique",
                "errors": f"Received {data.name} is already exists",
            },
        )

    validate_map(
        data=data,
        validators={
            "name": Pattern.ADDRESS_REGX,
            "description": Pattern.ADDRESS_REGX,
            "buy_price": Pattern.NUM_REGEX,
            "sell_price": Pattern.NUM_REGEX,
            "mrp": Pattern.NUM_REGEX,
            "hsn_code": Pattern.HSN_REGEX,
            "gst": Pattern.NUM_REGEX,
            "quantity": Pattern.NUM_REGEX,
            "unit": Pattern.UNIT_REGEX,
            "brand": Pattern.NAME_REGX,
            "model": Pattern.NAME_REGX,
            "image": Pattern.IMAGE_REGX,
        },
    )

    product = Product(
        name=data.name,
        description=data.description,
        buy_price=data.buy_price,
        sell_price=data.sell_price,
        mrp=data.mrp,
        hsn_code=data.hsn_code,
        gst=data.gst,
        quantity=data.quantity,
        unit=data.unit,
        brand=data.brand,
        model=data.model,
        image=data.image,
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Failed to create product",
                "errors": "Database Error: " + str(e),
            },
        )

    return product


def update_product(db: Session, product_id: int, data: ProductUpdate) -> Product:
    """
    Service for updating the product data with some validations
    """
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Product not found", "errors": None},
        )

    validate_map(
        data=data,
        validators={
            "name": Pattern.ADDRESS_REGX,
            "description": Pattern.ADDRESS_REGX,
            "buy_price": Pattern.NUM_REGEX,
            "sell_price": Pattern.NUM_REGEX,
            "mrp": Pattern.NUM_REGEX,
            "hsn_code": Pattern.HSN_REGEX,
            "gst": Pattern.NUM_REGEX,
            "quantity": Pattern.NUM_REGEX,
            "unit": Pattern.UNIT_REGEX,
            "brand": Pattern.NAME_REGX,
            "model": Pattern.NAME_REGX,
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

    if data_dict.get("name") and data_dict["name"] != product.name:
        exists = db.execute(
            select(Product).where(
                Product.name == data_dict["name"],
                Product.id != product.id,
            )
        ).scalar_one_or_none()

        if exists:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "msg": "Product name must be unique",
                    "errors": f"Product name '{data_dict["name"]}' already exists",
                },
            )

    for field, value in data_dict.items():
        setattr(product, field, value)

    try:
        product.last_updated = datetime.now(timezone.utc)
        db.commit()
        db.refresh(product)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Failed to update product",
                "errors": f"Database error: {str(e)}",
            },
        )

    return product


def delete_product(db: Session, product_id) -> None:
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"msg": "Product not found", "errors": None},
        )

    try:
        db.delete(product)
        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "msg": "Failed to delete product",
                "errors": f"Database error: {str(e)}",
            },
        )

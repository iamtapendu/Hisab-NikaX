from typing import Annotated
from fastapi import APIRouter, Body, Depends, Path, Query, status
from sqlalchemy.orm import Session

from core.common import ErrorResponse, PaginatedResponse
from dependencies.auth import required_roles
from dependencies.db import get_db
from modules.products import service as product_service
from .schema import ProductBase, ProductRead, ProductUpdate

router = APIRouter(tags=["Products"])


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[ProductRead],
    dependencies=[Depends(required_roles("admin", "manager", "staff"))],
    summary="Retrieve a paginated list of all products",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_products(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """
    Retrieve a paginated list of all products.

    This endpoint returns product records in paginated form, helping the frontend
    efficiently load products in pages (e.g., 50 per request) instead of fetching
    all records at once.

    Access Control:
    --------------
    - **Admin**: Can fetch all the product data
    - **Manager**: Can fetch all the product data
    - **Staff**: Can fetch all the product data
    """

    data, meta = product_service.get_products(db, page, per_page)
    return {
        "data": data,
        "meta": meta,
    }


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[ProductRead],
    dependencies=[Depends(required_roles("admin", "manager", "staff"))],
    summary="Search products with optional filters",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def search_products(
    db: Annotated[Session, Depends(get_db)],
    keywords: Annotated[
        str | None,
        Query(
            description="Free-text search (e.g. 'red small front')",
            max_length=200,
        ),
    ] = None,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    per_page: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 50,
    min_price: Annotated[float | None, Query(ge=0,le=999999, description="Minimum selling price")] = None,
    max_price: Annotated[float | None, Query(ge=0,le=999999, description="Maximum selling price")] = None,
    in_stock: Annotated[bool | None, Query(description="Only products in stock")] = None,
    brand: Annotated[str | None, Query(max_length=50, description="Brand name")] = None,
    unit: Annotated[
        str | None,
        Query(
            pattern=r"^(pcs|kg|gram|grs|ltr|ml|box|pkt|set|dozen)$",
            description="Unit of measurement",
        ),
    ] = None,
):
    """
    Search products using free-text keywords and structured filters.

    Examples:
    ---------
    - `/products/search?keywords=red small front`
    - `/products/search?brand=samsung&min_price=10000&max_price=30000`
    - `/products/search?keywords=charger&in_stock=true`

    Access Control:
    --------------
    - **Admin**: Can fetch all the product data
    - **Manager**: Can fetch all the product data
    - **Staff**: Can fetch all the product data
    """
    data, meta = product_service.search_products(
        db,
        keywords=keywords,
        page=page,
        per_page=per_page,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        brand=brand,
        unit=unit,
    )

    return {
        "data": data,
        "meta": meta,
    }


@router.get(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductRead,
    dependencies=[Depends(required_roles("admin", "manager", "staff"))],
    summary="Retrieve a single product by ID.",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        404: {"model": ErrorResponse, "description": "Product not found"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def get_product(
    db: Annotated[Session, Depends(get_db)],
    product_id: Annotated[int, Path(description="Product id", ge=1)],
):
    """
    Retrieve a single product by ID. Fetches a specific product from the
    database using their unique primary key.

    Access Control:
    --------------
    - **Admin**: Can fetch all the product data
    - **Manager**: Can fetch all the product data
    - **Staff**: Can fetch all the product data
    """
    return product_service.get_product(db, product_id)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ProductRead,
    dependencies=[Depends(required_roles("admin", "manager"))],
    summary="Create new product",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        409: {"model": ErrorResponse, "description": "Product name already exists"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def create_product(
    db: Annotated[Session, Depends(get_db)],
    payload: Annotated[ProductBase, Body(description="new product data")],
):
    """
    Create a new product in the system.

    This endpoint allows to create new products. Only fields that are
    provided and pass regex validation will be assigned; all other fields fall back
    to SQLAlchemy model defaults. Duplicate product name checks are performed before
    product creation.

    Access Control:
    --------------
    - **Admin**: Can fetch all the product data
    - **Manager**: Can fetch all the product data
    """
    return product_service.create_product(db, payload)


@router.put(
    "/{product_id}",
    status_code=status.HTTP_200_OK,
    response_model=ProductRead,
    dependencies=[Depends(required_roles("admin", "manager"))],
    summary="Update new product",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        404: {"model": ErrorResponse, "description": "Product not found"},
        409: {"model": ErrorResponse, "description": "Product name already exists"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def update_product(
    db: Annotated[Session, Depends(get_db)],
    product_id: Annotated[int, Path(description="product id", ge=1)],
    payload: Annotated[ProductUpdate, Body(description="Updated values")],
):
    """
     Update an existing product's information.

     This endpoint allows products and administrators to update specific product fields.
     Only the fields included in the incoming JSON payload will be updated. Each field is
     validated against its corresponding regex pattern before being saved.

    Access Control:
    --------------
    - **Admin**: Can fetch all the product data
    - **Manager**: Can fetch all the product data
    """
    return product_service.update_product(db, product_id, payload)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(required_roles("admin"))],
    summary="Delete a product",
    responses={
        403: {"model": ErrorResponse, "description": "Don't have enough permission"},
        404: {"model": ErrorResponse, "description": "Product not found"},
        422: {"model": ErrorResponse, "description": "Not able to process"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
def delete_product(
    db: Annotated[Session, Depends(get_db)],
    product_id: Annotated[int, Path(description="product id", ge=1)],
):
    """
    Delete a product by ID.

    This endpoint permanently removes a product record from the database based on
    the provided product ID.

    Access Control:
    --------------
    - **Admin**: Can fetch all the product data
    """
    return product_service.delete_product(db, product_id)

from flask import request
from sqlalchemy import select, func, or_
from .model import Product
from . import products_bp
from extensions import (
    db,
    role_required,
    validate_field,
    make_response,
    ADDRESS_REGX,
    NUM_REGEX,
    HSN_REGEX,
    UNIT_REGEX,
    IMAGE_REGX,
)

# Products fileds and thier respective regex
fields = {
    "name": ADDRESS_REGX,  # appropiate for product name
    "description": ADDRESS_REGX,  # appropiate for product description
    "buy_price": NUM_REGEX,
    "sell_price": NUM_REGEX,
    "mrp": NUM_REGEX,
    "hsn_code": HSN_REGEX,
    "gst": NUM_REGEX,
    "quantity": NUM_REGEX,
    "unit": UNIT_REGEX,
    "brand": ADDRESS_REGX,
    "model": ADDRESS_REGX,
    "image": IMAGE_REGX,
}


@products_bp.get("/")
@role_required("admin", "manager", "staff")
def get_products():
    """
    Retrieve a paginated list of all products.

    This endpoint returns product records in paginated form, helping the frontend
    efficiently load products in pages (e.g., 50 per request) instead of fetching
    all records at once.

    Access:
    -------
        Admin, Manager and staff only

    URL Params:
    -----------
        page : int (optional)
            The page number to retrieve. Default is 1.
        per_page : int (optional)
            Number of product records per page. Default is 50.

    JSON Payload:
    -------------
        None

    Error Responses:
    ----------------
        403 Forbidden
            Returned if the requesting user does not have access.

    Return:
    -------
        JSON Response
    """
    # Pagination metadata
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    # Paginate product
    stmt = select(Product).order_by(Product.id).offset((page - 1) * per_page).limit(per_page)
    products = db.session.execute(stmt).scalars().all()

    total = db.session.execute(select(func.count()).select_from(Product)).scalar()
    pages = (total + per_page - 1) // per_page if total else 0

    pg_dict = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": pages,
    }

    return make_response(
        data=[u.to_dict() for u in products],
        message="Successfully retrive data.",
        pagination=pg_dict,
    )


@products_bp.get("/<int:product_id>")
@role_required("admin", "manager", "staff")
def get_product(product_id: int):
    """
    Retrieve a single product by ID. Fetches a specific product from the
    database using their unique primary key.

    Access:
    -------
        Admin, Manager and staff only

    URL Params:
    -----------
        product_id (int)
            The unique ID of the product to retrieve.

    JSON Payload:
    --------------
        None

    Error Responses:
    ----------------
        404 Not Found
            Returned if no product exists with the given ID.
        403 Forbidden
            Returned if the requesting user does not have access.

    Return:
    -------
        200 OK
            A JSON object representing the serialized product record.
    """
    product = db.session.execute(
        select(Product).where(Product.id == product_id)
    ).scalar_one_or_none()

    if product is None:
        return make_response(
            message="Not able to fetch data.",
            errors="Product not found",
            status="fail",
            code=404,
        )

    return make_response(
        data=product.to_dict(),
        message="Successfully retrive data.",
    )


@products_bp.get("/search")
@role_required("admin", "manager", "staff")
def search_products():
    """
    Search products with optional filters and pagination.

    Supports searching by:
        - keyword (matches name, brand, model)

    Pagination supported using:
        ?page=1&per_page=20

    Access:
    -------
        Admin, Manager and staff only

    URL Params:
    -----------
        None

    JSON Payload:
    --------------
        None

    Error Responses:
    ----------------
        403 Forbidden
            Returned if the requesting user does not have access.

    Return:
    -------
        200 OK
            products lists
    """

    # Query params
    keyword = request.args.get("q", "", type=str).strip()
    per_page = request.args.get("per_page", 50, type=int)

    stmt = select(Product)

    # Keyword match
    if keyword:
        like = "%" + "%".join(keyword) + "%"
        stmt = stmt.where(
            or_(
                Product.name.ilike(like),
                Product.brand.ilike(like),
                Product.model.ilike(like),
                Product.description.ilike(like),
            )
        )

    # Pagination using limit
    stmt = stmt.limit(per_page)

    result = db.session.execute(stmt).scalars().all()

    return make_response(
        data=[p.to_dict() for p in result],
        message="Products retrieved successfully.",
    )


@products_bp.post("/")
@role_required("admin", "manager")
def create_product():
    """
    Create a new product in the system.

    This endpoint allows to create new products. Only fields that are
    provided and pass regex validation will be assigned; all other fields fall back
    to SQLAlchemy model defaults. Duplicate product name checks are performed before
    product creation.

    Access:
    -------
        Admin and manager only.

    JSON Payload:
    ------------
        {
            "name": "string (required, unique) — product name",
            "description": "string (optional) — product description",
            "buy_price": "number or numeric-string (required)",
            "sell_price": "number or numeric-string (required)",
            "mrp": "number or numeric-string (optional)",
            "hsn_code": "string (optional)",
            "gst": "number or numeric-string (optional)",
            "quantity": "number or numeric-string (optional)",
            "unit": "string (optional) — unit of measurement",
            "brand": "string (optional)",
            "model": "string (optional)",
            "image": "string (optional) — image URL or filename"
        }

    Error Responses:
    ----------------
        - 201 Created: Product successfully created.
        - 400 Bad Request: Validation error or missing required fields.
        - 409 Conflict: Product name already exists.

    Return:
    -------
        JSON response containing the created product data.

    """
    data = request.get_json()

    # Validate required fields
    if not data.get("name") or not data.get("buy_price") or not data.get("sell_price"):
        return make_response(
            message="Not able to create product.",
            errors="Missing mandatory fields",
            status="fail",
            code=400,
        )

    # Check product name uniqueness
    if db.session.execute(select(Product).where(Product.name == data.get("name"))).scalar():
        return make_response(
            message="Not able to create product.",
            errors="Product name already exists.",
            status="fail",
            code=409,
        )

    try:
        # Create new product object
        new_product = Product()

        # Setting values only those are matching with regex pattern
        for field, pattern in fields.items():
            value = validate_field(data.get(field), pattern, field)
            if value is not None:
                setattr(new_product, field, value)

    except ValueError as e:
        # Regex validation error
        return make_response(
            message="Not able to create product.",
            errors=str(e),
            status="fail",
            code=400,
        )

    # Save to database
    db.session.add(new_product)
    db.session.commit()

    return make_response(
        data=new_product.to_dict(),
        message="Successfuly created new product.",
        code=201,
    )


@products_bp.put("/<int:product_id>")
@role_required("admin", "manager")
def update_product(product_id: int):
    """
    Update an existing product's information.

    This endpoint allows products and administrators to update specific product fields.
    Only the fields included in the incoming JSON payload will be updated. Each field is
    validated against its corresponding regex pattern before being saved.

    Access:
    -------
        Admin and manager only

    URL Params:
    -----------
        product_id (int): Unique ID of the product to update.

    JSON Payload:
    -------------
        {
            "name": "string (required, unique) — product name",
            "description": "string (optional) — product description",
            "buy_price": "number or numeric-string (required)",
            "sell_price": "number or numeric-string (required)",
            "mrp": "number or numeric-string (optional)",
            "hsn_code": "string (optional)",
            "gst": "number or numeric-string (optional)",
            "quantity": "number or numeric-string (optional)",
            "unit": "string (optional) — unit of measurement",
            "brand": "string (optional)",
            "model": "string (optional)",
            "image": "string (optional) — image URL or filename"
        }

    Error Responses:
    ----------------
        - 400: Invalid field format (regex failure)
        - 403: Forbidden Returned if the requesting user does not have access.
        - 404: Product ID not found
        - 409: Product name already exists

    Return:
    -------
        json reponse containing updated product data.

    """
    product = db.session.execute(
        select(Product).where(Product.id == product_id)
    ).scalar_one_or_none()

    if product is None:
        return make_response(
            message="Not able to fetch data.",
            errors="Product not found",
            status="fail",
            code=404,
        )

    data = request.get_json()

    try:
        # validation for productname
        if validate_field(data.get("name"), ADDRESS_REGX, "name"):

            # checking whether new and old product name same or not
            if product.name != data.get("name"):
                if db.session.execute(
                    select(Product).where(Product.name == data.get("name"))
                ).scalar():
                    return make_response(
                        message="Not able to update product.",
                        errors="Product name already exists.",
                        status="fail",
                        code=409,
                    )

        # Setting values only those are matching with regex pattern
        for field, pattern in fields.items():
            value = validate_field(data.get(field), pattern, field)

            if value is not None:
                setattr(product, field, value)

    except ValueError as e:
        # Regex validation error
        return make_response(
            message="Not able to update product.",
            errors=str(e),
            status="fail",
            code=400,
        )

    # Commit changes
    db.session.commit()

    return make_response(
        data=product.to_dict(),
        message="Successfuly updated product.",
        code=200,
    )


@products_bp.delete("/<int:product_id>")
@role_required("admin")
def delete_product(product_id: int):
    """
    Delete a product by ID.

    This endpoint permanently removes a product record from the database based on
    the provided product ID.

    Access:
    -------
        Admin only

    URL Params:
    -----------
        product_id (int)
            The unique ID of the product to delete.

    JSON Payload:
    --------------
        None

    Error Responses:
    -----------------
        - 404 Not Found
            Returned if the product with the given ID does not exist.
        - 403 Forbidden
            Returned if the requesting user does not have access.


    Return:
    -------
        200 OK
            JSON object containing a success message.
    """

    product = db.session.execute(
        select(Product).where(Product.id == product_id)
    ).scalar_one_or_none()

    if product is None:
        return make_response(
            message="Not able to fetch data.",
            errors="Product not found",
            status="fail",
            code=404,
        )

    db.session.delete(product)
    db.session.commit()

    return make_response(
        message="Successfuly deleted product.",
        code=200,
    )

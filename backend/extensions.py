from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_identity
from functools import wraps
from flask import jsonify
import re

# Initialize shared Flask extensions (attached to the app in create_app)
db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

# Token blacklist
blacklist = set()

# Username:
#  - 3–20 characters
#  - letters, digits, underscore, dot
#  - cannot start/end with dot or underscore
USERNAME_REGX = r"^(?=.{3,20}$)(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$"

# Name:
#  - alphabets + spaces
#  - supports Indian names (no numbers/symbols)
NAME_REGX = r"^[A-Za-z][A-Za-z ]{1,49}$"

# Email:
EMAIL_REGX = (
    r"^(?!.*\.\.)"
    r"([A-Za-z0-9_+%-]+(?:\.[A-Za-z0-9_+%-]+)*)"
    r"@"
    r"([A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?)*)"
    r"\.[A-Za-z]{2,5}$"
)

# Phone:
#  - Indian mobile numbers
PHONE_REGX = r"^[6-9]\d{9}$"

# Password:
#  - Minimum 8 characters
#  - At least 1 uppercase, 1 lowercase, 1 digit, 1 special char
PASSWORD_REGX = (
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)" r"(?=.*[@$!%*?&#^])[A-Za-z\d@$!%*?&#^]{8,}$"
)

# Role:
#   "admin", "manager", "staff", "guest"
ROLE_REGX = r"admin|manager|staff|guest"

# Image filename:
#  - only JPG/PNG/JPEG
#  - prevents directory traversal
IMAGE_REGX = r"^[A-Za-z0-9_\-]+\.(jpg|jpeg|png)$"

# Address:
#  - Letters, digits, commas, slashes, hyphens, spaces
#  - Suitable for Indian address formatting
ADDRESS_REGX = r"^[A-Za-z0-9\s,./\-]{5,200}$"

# GST Number:
# Format:
#  - 15 characters
#  - 2 digit state code
#  - 10-digit PAN
#  - 1 entity code (1–9 or A–Z)
#  - 1 checksum character
GST_REGX = r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$"

# Aadhaar:
#  - 12 digits
#  - cannot start with 0 or 1
ADHAAR_REGX = r"^[2-9]\d{11}$"

# Bank Account Number:
#  - 9 to 18 digits (Indian banks support wide range)
BANK_REGX = r"^\d{9,18}$"

# IFSC Code:
# Format:
#  - 4 uppercase letters (bank code)
#  - 0
#  - 6 digits
# Example: SBIN0005943
IFSC_REGX = r"^[A-Z]{4}0[0-9]{6}$"

# PAN (Permanent Account Number)
# - 5 letters
# - 4 digits
# - 1 letter
PAN_REGX = r"^[A-Z]{5}\d{4}[A-Z]$"


def role_required(*roles):
    """
    A decorator to restrict access to specific user roles using JWT authentication.

    This decorator ensures that:
    1. A valid JWT access token is present in the request.
    2. The user identity extracted from the JWT contains a "role" field.
    3. Only users whose roles match the allowed roles passed to the decorator
       can access the protected endpoint.

    Parameters
    ----------
    *roles* : str
        One or more role names that are allowed to access the decorated route.
        Example:
            @role_required("admin")
            @role_required("admin", "manager")

    How It Works
    ------------
    - The decorator first verifies the JWT in the incoming request using
      `verify_jwt_in_request()`. If the token is invalid or missing,
      Flask-JWT-Extended handles the error response automatically.

    - After verification, it retrieves the user identity using
      `get_jwt_identity()`, which is expected to return a dictionary containing
      user information (including the user's role).

    - The user's role is checked against the allowed roles. If the role is not
      permitted, the decorator returns a 403 (Forbidden) response.

    Returns
    -------
    function
        The wrapped view function which executes only if the user is authorized.

    Example
    -------
    @app.route("/admin/dashboard")
    @role_required("admin")
    def admin_dashboard():
        return {"message": "Welcome, Admin!"}

    @app.route("/staff/reports")
    @role_required("admin", "manager")
    def view_reports():
        return {"message": "Reports accessible."}
    """

    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):

            # ------------------------------
            # Step 1: Validate JWT token
            # If JWT is missing or invalid, Flask-JWT-Extended will return
            # a 401/422 response automatically.
            # ------------------------------
            verify_jwt_in_request()

            # ------------------------------
            # Step 2: Extract user identity from the token payload.
            # It's expected that the identity contains a "role" field:
            # Example payload: {"id": 1, "email": "...", "role": "admin"}
            # ------------------------------
            user = get_jwt_identity()
            user_role = user.get("role")

            # ------------------------------
            # Step 3: Check if the user's role is authorized for this route.
            # If not authorized → return a 403 Forbidden response.
            # ------------------------------
            if user_role not in roles:
                return (
                    jsonify(
                        {
                            "error": "Access denied. You are not authorized for this action."
                        }
                    ),
                    403,
                )

            # ------------------------------
            # Step 4: The user is authorized → proceed with the endpoint logic.
            # ------------------------------
            return fn(*args, **kwargs)

        return decorator

    return wrapper


def validate_field(value, pattern, field_name):
    """
    Validate a field value against a given regular expression pattern.

    This function is used for input validation before saving data to the
    database. If the value is not provided (None), the function returns None,
    allowing SQLAlchemy to apply model defaults. If a value is provided but
    does not match the supplied regex pattern, a ValueError is raised. This
    ensures consistent validation logic across routes and prevents invalid
    data from being stored.

    Args:
        value (Any): The incoming value from request JSON. Can be None or any type.
        pattern (str): A regular expression used to validate the value.
        field_name (str): The name of the field being validated, used to generate
                          meaningful error messages.

    Returns:
        Any: The original value if validation succeeds or None if no value
             was provided.

    Raises:
        ValueError: If the value is provided but does not match the regex pattern.

    Examples:
        >>> validate_field("john_doe", USERNAME_REGEX, "username")
        'john_doe'

        >>> validate_field(None, EMAIL_REGEX, "email")
        None  # field not provided, model default will apply

        >>> validate_field("wrong@", EMAIL_REGEX, "email")
        ValueError: Invalid email.
    """
    if value is None or str(value).strip() == "":
        return None  # field not provided, let model defaults apply

    value = str(value).strip()
    if not re.fullmatch(pattern, value):
        raise ValueError(f"Invalid {field_name}.")

    return value


def make_response(
    data=None, message="", status="success", code=200, errors=None, pagination=None
):
    """
    Generate a structured JSON response APIs.

    Args:
    -----
        data (dict/list, optional): The main response data.
        message (str, optional): Human-readable message.
        status (str): "success" or "error".
        code (int): HTTP status code.
        errors (dict, optional): Validation or other error details.
        pagination (dict, optional): Pagination metadata:
            - page: current page number
            - per_page: items per page
            - total: total items
            - pages: total pages

    Returns:
    -------
        tuple: Usage

    Examples:
    ---------------
        - Simple success response
        >>> return make_response(data={"id": 1, "username": "john"}, message="User fetched")

        - Error response
        >>> return make_response(message="Validation failed", status="error", code=400,
                            errors={"username": "Required"})

        - Paginated response
        >>> pagination = {
            "page": 1,
            "per_page": 10,
            "total": 100,
            "pages": 10
        }
        return make_response(data=[...], message="Users fetched", pagination=pagination)
    """
    response = {
        "status": status,
        "code": code,
        "message": message,
        "data": data,
        "errors": errors,
        "pagination": pagination,
    }
    return response, code

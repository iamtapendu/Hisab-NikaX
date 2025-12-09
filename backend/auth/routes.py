from flask import request
from extensions import db, role_required, validate_field, make_response, blacklist,\
    USERNAME_REGX, NAME_REGX, EMAIL_REGX, PHONE_REGX, PASSWORD_REGX, ROLE_REGX, IMAGE_REGX
from flask_jwt_extended import create_access_token, create_refresh_token,\
    jwt_required, get_jwt_identity, get_jwt, decode_token
from sqlalchemy import select
from users.model import User
from . import auth_bp

# Users fileds and thier respective regex
fields = {
    "username": USERNAME_REGX,
    "name": NAME_REGX,
    "email": EMAIL_REGX,
    "phone": PHONE_REGX,
    "role": ROLE_REGX,
    "image": IMAGE_REGX,
    "password": PASSWORD_REGX
}

@auth_bp.post("/register")
def register():
    """
    Register a new user into the system.

    This endpoint creates a new user account after validating all input fields
    using regex patterns and ensuring mandatory fields are present. The role is 
    forced to its default value and password is stored after hashing.

    Access:
    -------
        Public (No authentication required)

    JSON Payload:
    -------------
        {
            "username": "john123",
            "password": "Test@123",
            "name": "John Doe",
            "email": "john@email.com",
            "phone": "9876543210",
            "image": "profile.png"
        }

    Error Responses:
    ----------------
        - 400: Missing mandatory fields / Invalid regex format
        - 409: Username already exists

    Return:
    -------
        JSON containing newly created user data and status code 201.
    """
    data = request.get_json()

    if not data.get("username") or not data.get("password") or not data.get("name"):
        return make_response(
            message="Not able to register user.",
            errors="Missing mandatory fields",
            status="fail",
            code=400
        )

    if db.session.execute(select(User).where(User.username == data.get("username"))).scalar():
        return make_response(
            message="Not able to register user.",
            errors="Username already exists.",
            status="fail",
            code=409
        )
    
    try:
        new_user = User()

        for field, pattern in fields.items():
            value = validate_field(data.get(field), pattern, field)
            if value is not None and field != "role":
                setattr(new_user, field, value)
    
    except ValueError as e:
        return make_response(
            message="Not able to register user.",
            errors=str(e),
            status="fail",
            code=400
        )

    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()

    return make_response(
        data=new_user.to_dict(),
        message="Successfuly registered new user.",
        code=201
    )


@auth_bp.post("/login")
def login():
    """
    Authenticate user and generate JWT tokens.

    This endpoint validates the provided username and password and returns
    both an access token and a refresh token upon successful login.

    Access:
    -------
        Public (No authentication required)

    JSON Payload:
    -------------
        {
            "username": "john123",
            "password": "Test@123"
        }

    Error Responses:
    ----------------
        - 400: Missing username/password or invalid credentials

    Return:
    -------
        {
            "access_token": "<JWT_ACCESS>",
            "refresh_token": "<JWT_REFRESH>"
        }
    """
    data = request.get_json()

    if not data.get("username") or not data.get("password"):
        return make_response(
            message="Not able to login.",
            errors="Missing username/password",
            status="fail",
            code=400
        )
    
    user = db.session.execute(select(User).where(User.username == data.get("username"))).scalar_one_or_none()

    if not user or not user.check_password(data.get("password")):
        return make_response(
            message="Not able to login",
            errors="Invalid username/password",
            status="fail",
            code=400
        )

    access_token = create_access_token(
        identity={"user_id":user.id, "role":user.role},
        additional_claims={"type": "access"}
    )
    refresh_token = create_refresh_token(
        identity={"user_id":user.id, "role":user.role},
        additional_claims={"type": "refresh"}
    )

    return make_response(
        data={"access_token":access_token,"refresh_token":refresh_token},
        message="Login successful."
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_token():
    """
    Generate a new access token using the refresh token.

    This endpoint is used when an access token has expired. The client 
    sends a valid refresh token to obtain a new access token.

    Access:
    -------
        Requires a valid refresh token

    JSON Payload:
    -------------
        None

    Error Responses:
    ----------------
        - 401: Missing or invalid refresh token

    Return:
    -------
        {
            "access_token": "<NEW_JWT_ACCESS>"
        }
    """
    identity = get_jwt_identity()
    access = create_access_token(identity=identity, additional_claims={"type": "access"})

    return make_response(
        data={"access_token": access},
        message="Token refreshed successfully."
    )


@auth_bp.post("/logout")
@jwt_required()
def logout():
    """
    Logout user by blacklisting both access and refresh tokens.

    The access token is obtained from the Authorization header.
    The refresh token must be passed in the request body and is decoded
    to extract its JTI for blacklisting.

    Access:
    -------
        Any authenticated user (valid access token required)

    JSON Payload:
    -------------
        {
            "refresh_token": "<JWT_REFRESH>"
        }

    Error Responses:
    ----------------
        - 400: Missing refresh token / Invalid token
        - 401: Missing or invalid access token

    Return:
    -------
        Simple success message after both tokens are blacklisted.
    """
    current_jti = get_jwt()["jti"]

    data = request.get_json() or {}
    refresh_token = data.get("refresh_token") or ""

    if not refresh_token:
        return make_response(
            message="Unable to logout.",
            errors="Refresh token is required.",
            status="fail",
            code=400
        )

    try:
        token = decode_token(refresh_token)
        if token["type"] != "refresh":
            raise Exception(f"Received {token["type"]} token") 
        
        refresh_jti = token["jti"]

        blacklist.add(current_jti)
        blacklist.add(refresh_jti)

    except Exception as e:
        return make_response(
            message="Unable to logout.",
            errors="Invalid refresh token: " + str(e),
            status="fail",
            code=400
        )

    return make_response(
        message="Logout successfully.",
        code=200
    )

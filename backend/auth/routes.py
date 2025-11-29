from flask import request
from extensions import db, role_required, validate_field, make_response,\
    USERNAME_REGX, NAME_REGX, EMAIL_REGX, PHONE_REGX, PASSWORD_REGX, ROLE_REGX, IMAGE_REGX
from flask_jwt_extended import create_access_token, create_refresh_token,\
    jwt_required, get_jwt_identity
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
    data = request.get_json()

    # Validate required fields
    if not data.get("username") or not data.get("password") or not data.get("name"):
        return make_response(
            message="Not able to register user.",
            errors="Missing mandatory fields",
            code=400
        )

    # Check username uniqueness
    if User.query.filter_by(username=data["username"]).first():
        return make_response(
            message="Not able to register user.",
            errors="Username already exists.",
            code=409
        )
    
    try:
        # Create new user object
        new_user = User()

        # Setting values only those are matching with regex pattern
        for field, pattern in fields.items():
            value = validate_field(data.get(field), pattern, field)
            if value is not None and field != "role":  # forcing role to assign deafult value at registration
                setattr(new_user, field, value)
    
    except ValueError as e:
        # Regex validation error
        return make_response(
            message="Not able to register user.",
            errors=str(e),
            code=400
        )

    # Hash and set password
    new_user.set_password(data["password"])

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return make_response(
        data=new_user.to_dict(),
        message="Successfuly registered new user.",
        code=201
    )

@auth_bp.post("/login")
def login():
    data = request.get_json()

    # Chgecking for missing data
    if data.get("username") or data.get("password"):
        return make_response(
            message="Not able to login.",
            errors="Missing username/password",
            code=400
        )
    
    user = User.query.filter_by(data.get("username")).first()

    # Checking username and corresponding password 
    if not user or not user.check_password(data.get("password")):
        return make_response(
            message="Not able to login",
            errors="Invalid username/password",
            code=400
        )

    # Creating access and refresh tokens
    access_token = create_access_token(identity={"user_id":user.id, "role":user.role})
    refresh_token = create_refresh_token(identity={"user_id":user.id, "role":user.role})

    return make_response(
        data={"access_token":access_token,"refresh_token":refresh_token},
        message="Login successful."
    )


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)

    return make_response(
        data={"access_token": access},
        message="Token refreshed successfully."
    )
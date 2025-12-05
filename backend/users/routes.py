from flask import request
from extensions import db, role_required, validate_field, make_response,\
    USERNAME_REGX, NAME_REGX, EMAIL_REGX, PHONE_REGX, PASSWORD_REGX, ROLE_REGX, IMAGE_REGX
from flask_jwt_extended import get_jwt_identity,jwt_required
from .model import User
from . import users_bp

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


@users_bp.get("/")
@role_required('admin')
def get_users():
    """
    Retrieve a paginated list of all users.

    This endpoint returns user records in paginated form, helping the frontend
    efficiently load users in pages (e.g., 50 per request) instead of fetching
    all records at once. Ideal for admin dashboards, management tables, and
    any screen displaying large datasets.

    Access:  
    -------
        Admin only

    URL Params:
    ----------- 
        page : int (optional)  
            The page number to retrieve. Default is 1.  
        per_page : int (optional)  
            Number of user records per page. Default is 50.

    JSON Payload:
    -------------
        None

    Error Responses:
    ----------------
        None

    Return:
    ------- 
        JSON Response
    """
    # Pagination metadata
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 50, type=int)

    # Paginate user query
    pagination = User.query.paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    pg_dict = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages
    }

    return make_response(
        data=[u.to_dict() for u in pagination.items],
        message="Successfully retrive data.",
        pagination=pg_dict   
    )


@users_bp.get("/<int:user_id>")
@jwt_required()
def get_user(user_id:int):
    """
    Retrieve a single user by ID.

    Fetches a specific user from the database using their unique primary key.
    Typically used for viewing user profiles, pre-filling edit forms, or
    administrative inspection of a particular user record.

    Access:
    -------
        Any one with valid credentials

    URL Params:
    -----------
        user_id (int)  
            The unique ID of the user to retrieve.

    JSON Payload:
    --------------
        None

    Error Responses:
    ----------------
        404 Not Found  
            Returned if no user exists with the given ID.
        403 Forbidden  
            Returned if the requesting user does not have admin access.

    Return:
    -------
        200 OK  
            A JSON object representing the serialized user record.
    """
    user_jwt = get_jwt_identity()
    if user_jwt["user_id"]!=user_id and user_jwt["role"]!="admin":
        return make_response(
            message="Not able to fetch data.",
            errors="requesting user does not have admin access",
            status="fail",
            code=403
        )
    
    user = User.query.get_or_404(user_id)
    return make_response(data=user.to_dict(),message="Successfully retrive data.")


@users_bp.get("/username/<username>")
@jwt_required()
def get_user_by_username(username:str):
    """
    Retrieve a single user by useranme.

    Fetches a specific user from the database using their unique username.
    Typically used for viewing user profiles, pre-filling edit forms, or
    administrative inspection of a particular user record.

    Access:
    -------
        Anyone with valid credentials

    URL Params:
    -----------
        username (str)  
            The unique ID of the user to retrieve.

    JSON Payload:
    --------------
        None

    Error Responses:
    ----------------
        404 Not Found  
            Returned if no user exists with the given username.
        403 Forbidden  
            Returned if the requesting user does not have admin access.

    Return:
    -------
        200 OK  
            A JSON object representing the serialized user record. 
    """
    username_jwt = User.query.get(get_jwt_identity()["user_id"]).username # type: ignore
    if username_jwt!=username and get_jwt_identity()["role"]!="admin":
        return make_response(
            message="Not able to fetch data.",
            errors="Requesting user does not have admin access",
            status="fail",
            code=403
        )
    # Get user or return 404
    user = User.query.filter_by(username=username).first_or_404()

    return make_response(data=user.to_dict(),message="Successfully retrive data.")


@users_bp.post("/")
@role_required('admin')
def create_user():
    """
    Create a new user in the system.

    This endpoint allows administrators to create new users. Only fields that are 
    provided and pass regex validation will be assigned; all other fields fall back 
    to SQLAlchemy model defaults. Duplicate username checks are performed before 
    user creation. Password is always required and stored in a securely hashed form.

    Access:
    -------  
        Admin only.

    JSON Payload:
    ------------
        {
            "username": "string (required)",
            "password": "string (required)",
            "name": "string (required)",
            "email": "string (optional)",
            "phone": "string or number (optional)",
            "role": "string (optional)",
            "image": "string (optional)"
        }

    Error Responses:
    ----------------
        - 201 Created: User successfully created.
        - 400 Bad Request: Validation error or missing required fields.
        - 409 Conflict: Username already exists.
    
    Return:
    -------
        JSON response containing the created user's data.

    """
    data = request.get_json()

    # Validate required fields
    if not data.get("username") or not data.get("password") or not data.get("name"):
        return make_response(
            message="Not able to create user.",
            errors="Missing mandatory fields",
            status="fail",
            code=400
        )

    # Check username uniqueness
    if User.query.filter_by(username=data["username"]).first():
        return make_response(
            message="Not able to create user.",
            errors="Username already exists.",
            status="fail",
            code=409
        )
    
    try:
        # Create new user object
        new_user = User()

        # Setting values only those are matching with regex pattern
        for field, pattern in fields.items():
            value = validate_field(data.get(field), pattern, field)
            if value is not None:
                setattr(new_user, field, value)
    
    except ValueError as e:
        # Regex validation error
        return make_response(
            message="Not able to create user.",
            errors=str(e),
            status="fail",
            code=400
        )

    # Hash and set password
    new_user.set_password(data["password"])

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return make_response(
        data=new_user.to_dict(),
        message="Successfuly created new user.",
        code=201
    )


@users_bp.put("/<int:user_id>")
@jwt_required()
def update_user(user_id):
    """
    Update an existing user's information.

    This endpoint allows users and administrators to update specific user fields such as 
    username, email, name, phone, role, image, and password. Only the fields 
    included in the incoming JSON payload will be updated. Each field is 
    validated against its corresponding regex pattern before being saved.

    Access:  
    -------
        Anyone with valid credentials

    URL Params: 
    ----------- 
        user_id (int): Unique ID of the user to update.

    JSON Payload:
    -------------
        {
            "username": "new_username",
            "email": "newmail@example.com",
            "name": "New Name",
            "phone": "9876543210",
            "role": "manager",
            "password": "NewPass123@"
        }

    Error Responses:
    ----------------
        - 400: Invalid field format (regex failure)
        - 403: Forbidden Returned if the requesting user does not have access.
        - 404: User ID not found
        - 409: Username/email already exists

    Return:
    ------- 
        json reponse containing updated users data.

    """

    user_jwt = get_jwt_identity()
    if user_jwt["user_id"]!=user_id and user_jwt["role"]!="admin":
        return make_response(
            message="Not able to update data.",
            errors="User does not have admin access",
            status="fail",
            code=403
        )

    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    try:
        # validation for username
        if validate_field(data.get("username"),USERNAME_REGX,'username'):
            if user.username != data.get("username"): # checking whether new and old username same or not 
                if User.query.filter_by(username=data["username"]).first():
                    return make_response(
                        message="Not able to update user.",
                        errors="Username already exists.",
                        status="fail",
                        code=409
                    )
        
        # Setting values only those are matching with regex pattern
        for field, pattern in fields.items():
            value = validate_field(data.get(field), pattern, field)
            if field == "password":
                continue
            elif field == "role" and user_jwt["role"]!="admin":
                continue
            elif value is not None:
                setattr(user, field, value)
    
    except ValueError as e:
        # Regex validation error
        return make_response(
            message="Not able to update user.",
            errors=str(e),
            status="fail",
            code=400
        )

    # Commit changes
    db.session.commit()

    return make_response(
        data=user.to_dict(),
        message="Successfuly updated user.",
        code=200
    )


@users_bp.put("/<int:user_id>/password")
@jwt_required()
def update_password(user_id):
    """
    This endpoint allows administrators to update password. 

    Access:  
    -------
        Anyone with valid credentials.

    URL Params: 
    ----------- 
        user_id: int

    JSON Payload:
    -------------
        {
            "old_password": "OldPass123@",
            "new_password": "NewPass123@"
        }

    Error Responses:
    ----------------
        - 400: Invalid field format (regex failure)
        - 403: Forbidden Returned if the requesting user does not have access.
        - 404: User ID not found
    
    Return:
    -------
        200 OK
            JSON reponse containing successfull response.
    """
    user_jwt = get_jwt_identity()
    data = request.get_json()
    
    # Mandatory data
    if not data.get("old_password") or not data.get("new_password"):
        return make_response(
            message="Not able to change password.",
            errors="Old and new password are required",
            status="fail",
            code=400
        )
    # Checking only admin or self password can be changed
    if user_id!= user_jwt["user_id"] and user_jwt["role"]!='admin':
        return make_response(
            message="Not able to change password.",
            errors="User does not have admin access",
            status="fail",
            code=403
        )
    
    user = User.query.get_or_404(user_id)
        
    # Check for old password correctness
    if not user.check_password(data.get("old_password")):
        return make_response(
            message="Not able to change password.",
            errors="Incorrect old password.",
            status="fail",
            code=400
        )

    # Check same password reuse
    if data.get("old_password") == data.get("new_password"):
        return make_response(
            message="Not able to change password.",
            errors="New password and old are same",
            status="fail",
            code=409
        )

    try:
        # validation for username
        if validate_field(data.get("new_password"),PASSWORD_REGX,'password'):
            user.set_password(data.get("new_password"))
    
    except ValueError as e:
        # Regex validation error
        return make_response(
            message="Not able to change password.",
            errors=str(e),
            status="fail",
            code=400
        )

    # Commit changes
    db.session.commit()

    return make_response(
        message="Successfuly chnaged user password.",
        code=200
    )

@users_bp.delete("/<int:user_id>")
@role_required('admin')
def delete_user(user_id):
    """
    Delete a user by ID.

    This endpoint permanently removes a user record from the database based on 
    the provided user ID. Typically used in admin dashboards for user 
    management and cleanup operations.

    Access:
    -------
        Admin only

    URL Params:
    -----------
        user_id (int)  
            The unique ID of the user to delete.

    JSON Payload:
    --------------
        None

    Error Responses:
    -----------------
        - 404 Not Found  
            Returned if the user with the given ID does not exist.
        - 403 Forbidden 
            Returned if the requesting user does not have access.


    Return:
    -------
        200 OK  
            JSON object containing a success message.
    """
    jwt = get_jwt_identity()
    if jwt["user_id"] == user_id:
        return make_response(
            message="Not able to delete user.",
            errors="Can not delete admin self account.",
            status="fail",
            code=400
        )
    user = User.query.get_or_404(user_id)

    db.session.delete(user)
    db.session.commit()

    return make_response(
        message="Successfuly deleted user.",
        code=200
    )



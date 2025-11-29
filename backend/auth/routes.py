from flask import request
from extensions import db, role_required, validate_field, make_response,\
    USERNAME_REGX, NAME_REGX, EMAIL_REGX, PHONE_REGX, PASSWORD_REGX, ROLE_REGX, IMAGE_REGX
from users.model import User
from . import auth_bp
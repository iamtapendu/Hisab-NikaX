from flask import Blueprint

# name: "auth" -> internal identifier for Flask
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

# Import routes at the end to avoid circular imports
# This will register all endpoint functions defined in routes.py with this blueprint
from . import routes

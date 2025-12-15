from flask import Blueprint

# name: "users" -> internal identifier for Flask
sales_bp = Blueprint("users", __name__, url_prefix="/api/sales")

# Import routes at the end to avoid circular imports
# This will register all endpoint functions defined in routes.py with this blueprint
from . import routes

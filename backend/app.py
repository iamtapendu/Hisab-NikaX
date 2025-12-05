from flask import Flask
from extensions import db, bcrypt, jwt, blacklist, make_response
from werkzeug.exceptions import NotFound
from flask_cors import CORS
from config import Config
import os


def create_app(config_class=Config):
    """
    Flask application factory.

    This function creates and configures a Flask application instance
    based on the given configuration class. It is a common pattern in
    Flask projects to support multiple environments (development,
    testing, production) and to enable modular app structure using
    Blueprints.

    Parameters
    ----------
    config_class : class, optional
        The configuration class to use for the Flask app.
        Defaults to DevelopmentConfig.

    Returns
    -------
    app : Flask
        Configured Flask application instance ready to run.
    """

    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)  # Load configuration from class

    # Enable Cross-Origin Resource Sharing (CORS)
    # Supports cookies and credentials for front-end requests
    CORS(app, supports_credentials=True)

    # Initialize Flask extensions
    # Attach SQLAlchemy, Bcrypt, and JWT to the app
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    # Import and register Blueprints
    # Each blueprint represents a modular component of the app
    from users.routes import users_bp
    from auth.routes import auth_bp
    # from Customer.routes import customer_bp
    # from Supplier.routes import supplier_bp
    # from Staff.routes import staff_bp
    # from Sale.routes import sale_bp
    # from Purchase.routes import purchase_bp
    # from Expense.routes import expense_bp
    # from Invoice.routes import invoice_bp
    # from Report.routes import report_bp

    app.register_blueprint(users_bp)
    app.register_blueprint(auth_bp)
    # app.register_blueprint(customer_bp)
    # app.register_blueprint(supplier_bp)
    # app.register_blueprint(staff_bp)
    # app.register_blueprint(sale_bp)
    # app.register_blueprint(purchase_bp)
    # app.register_blueprint(expense_bp)
    # app.register_blueprint(invoice_bp)
    # app.register_blueprint(report_bp)

    @app.errorhandler(NotFound)
    def handle_404(e):
        return make_response(
            message="Resource not found",
            status="fail",
            code=404,
            errors=str(e)
        )
    
    @jwt.token_in_blocklist_loader
    def is_token_revoked(jwt_header, jwt_payload):
        return jwt_payload["jti"] in blacklist

    return app

# Entry point to run the app
if __name__ == "__main__":
    # Create the app using the factory
    app = create_app()

    # Ensure the database tables are created
    # This runs only when the script is executed directly
    with app.app_context():
        db.create_all()

    # Start the Flask development server
    # Use environment variables to configure host/port in production
    app.run()

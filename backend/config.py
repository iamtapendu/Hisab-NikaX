import os

# Base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class for Flask applications.

    Contains default settings common across all environments.

    Attributes
    ----------
    SECRET_KEY : str
        Secret key for Flask sessions and CSRF protection.
        Default: 'secretkey', should be overridden in production.
    
    SQLALCHEMY_TRACK_MODIFICATIONS : bool
        Whether to track modifications of objects and emit signals.
        Default: False for better performance.
    
    JWT_SECRET_KEY : str
        Secret key used by Flask-JWT-Extended for signing tokens.
        Default: 'supersecret', should be overridden in production.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "secretkey")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")


class DevelopmentConfig(Config):
    """
    Development configuration.

    Use this configuration during development. Enables debug mode
    and uses a local SQLite database by default.
    
    Attributes
    ----------
    DEBUG : bool
        Enables Flask debug mode for detailed error messages.
    
    SQLALCHEMY_DATABASE_URI : str
        URI for the development database.
        Default: SQLite file 'database/app.db'.
    """

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database', 'app.db')}"


class ProductionConfig(Config):
    """
    Production configuration.

    Use this configuration in production environment. 
    Ensure environment variables are properly set for sensitive keys.
    
    Attributes
    ----------
    SQLALCHEMY_DATABASE_URI : str
        URI for the production database.
        Default: SQLite file 'Database/prod.db' if no environment variable provided.
    
    SECRET_KEY : str
        Should always be set via environment variable in production.
    
    JWT_SECRET_KEY : str
        Should always be set via environment variable in production.
    """

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(basedir, 'database', 'app.db')}"
    )
    DEBUG = False  # Ensure debug mode is off in production


class TestConfig(Config):
    """
    Testing configuration for running pytest or other test suites.

    Overrides base configuration for testing purposes.
    - Uses an in-memory SQLite database.
    - Sets TESTING mode to True.
    - Provides a simple JWT secret key for test tokens.
    """

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_SECRET_KEY = "test-jwt-secret"

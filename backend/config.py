import os
from datetime import timedelta

# Base directory of the project
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Base configuration class for Flask applications.

    Contains default settings common across all environments.

    Attributes
    ----------
    SECRET_KEY : str
        Secret key used by Flask for securely signing session cookies
        and protecting against CSRF attacks. It should be changed
        in production to a long, unpredictable value. Default is
        taken from the environment variable `SECRET_KEY`, otherwise
        'secretkey' is used.

    SQLALCHEMY_TRACK_MODIFICATIONS : bool
        Determines whether SQLAlchemy will track object modifications
        and emit signals. Enabling this adds overhead and is not needed
        for most applications. Default is False for better performance.

    JWT_SECRET_KEY : str
        The secret key used internally by Flask-JWT-Extended to sign
        and verify JWT access and refresh tokens. This must be secure
        in production, ideally set using an environment variable.
        Default comes from `JWT_SECRET_KEY`, otherwise 'supersecret'.

    JWT_ACCESS_TOKEN_EXPIRES : datetime.timedelta
        Configures the lifespan of generated access tokens. Once expired,
        the user must request a new access token using a refresh token.
        The default is 30 minutes, making access tokens short-lived and
        secure for API calls.

    JWT_REFRESH_TOKEN_EXPIRES : datetime.timedelta
        Determines how long refresh tokens remain valid. Refresh tokens
        are used to obtain new access tokens without logging in again.
        The default is 24 hours, meaning users can stay authenticated
        for an entire day without re-entering their credentials.

    JWT_BLACKLIST_ENABLED : bool
        Enables token blacklisting functionality in Flask-JWT-Extended.
        When set to True, the application can invalidate tokens manually
        (e.g., during a logout) by storing them in a blacklist.

    JWT_BLACKLIST_TOKEN_CHECKS : list[str]
        Specifies which token types should be checked against the blacklist.
        Options are "access", "refresh", or both. By default, both access
        and refresh tokens are verified, ensuring that any explicitly revoked
        token cannot be used again.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "secretkey")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecret")
    JWT_IDENTITY_CLAIM = "identity"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ["access", "refresh"]
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(basedir, 'database', 'app.db')}"


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
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'database', 'app.db')}"
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
    PROPAGATE_EXCEPTIONS = False

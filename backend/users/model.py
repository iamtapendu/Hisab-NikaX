from extensions import db, bcrypt
from datetime import datetime, timezone


class User(db.Model):
    """
    User model representing the application's users.

    This model stores information about users including login credentials,
    contact information, roles, and status.

    Columns
    -------
    id : Integer
        Primary key for the user table.
    username : String(20)
        Unique username used for login.
    name : String(50)
        Full name of the user.
    email : String(50)
        User's email address.
    phone : String(10)
        User's phone number.
    password_hash : String(200)
        Hashed password for secure authentication.
    role : String(50)
        Role of the user for authorization. Default: "guest".
    image : String(50)
        Profile image filename or path. Default: empty string.
    created_at : DateTime
        Timestamp of when the user was created. Default: current UTC time.

    Methods
    -------
    set_password(password)
        Hashes the provided password and stores it in password_hash.
    check_password(password)
        Checks a plaintext password against the stored hash.
    to_dict()
        Serializes the user object to a dictionary for JSON responses.
    """

    __tablename__ = "users"

    # Table columns
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50))
    phone = db.Column(db.String(10))

    password_hash = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), default="guest", nullable=False)

    image = db.Column(db.String(50), default="")

    # Use utc to ensure timezone-independent creation timestamp
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Password handling
    def set_password(self, password):
        """
        Hashes the plaintext password and stores it in `password_hash`.

        Parameters
        ----------
        password : str
            Plaintext password provided by the user.
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode()

    def check_password(self, password):
        """
        Verifies if the provided password matches the stored hash.

        Parameters
        ----------
        password : str
            Plaintext password to verify.

        Returns
        -------
        bool
            True if password matches, False otherwise.
        """
        return bcrypt.check_password_hash(self.password_hash, password)

    # Serialization for API responses
    def to_dict(self):
        """
        Converts the User object into a dictionary suitable for JSON responses.

        Returns
        -------
        dict
            Dictionary containing user data (excluding password hash).
        """
        return {
            "id": self.id,
            "username": self.username,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "role": self.role,
            "created_at": self.created_at.isoformat(),
            "image": self.image,
        }

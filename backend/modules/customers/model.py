from backend.dependecies.extensions import db
from datetime import datetime, timezone


class Customer(db.Model):
    """
    Represents a customer record in the system.

    This model stores key customer details such as contact information,
    identity numbers, bank details, and profile image. It is used for
    customer management modules, invoicing systems, and any feature that
    requires retrieving or updating customer information.

    Columns
    -------
    id : Integer
        Primary key for the customer.
    name : String(50)
        Full name of the customer. Required.
    address : String(256)
        Customer's residential or business address.
    email : String(50)
        Customer's email address.
    phone : String(10)
        Customer's mobile number (10 digits).
    gst : String(15)
        GST identification number for business customers.
    adhaar : String(12)
        Aadhaar number (12 digits) for identification.
    pan : String(10)
        PAN number for tax purposes.
    bank_ac : String(18)
        Customer's bank account number.
    bank_ifsc : String(11)
        Bank IFSC code for identifying the branch.
    image : String(50)
        Filename or path of the customer's profile image.
        Defaults to an empty string.
    created_at : DateTime
        Timestamp when the customer record was created.
        Defaults to the current UTC time.

    Relationships
    -------------
        invoices: List of invoices in Invoices table.

    Methods
    -------
    to_dict()
        Serializes the customer object into a dictionary suitable for JSON
        API responses. Useful for returning customer details to the frontend.
    """

    __tablename__ = "customers"

    # Table columns
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.Text)
    email = db.Column(db.String(50))
    phone = db.Column(db.String(10))

    gst = db.Column(db.String(15))
    adhaar = db.Column(db.String(12))

    pan = db.Column(db.String(10))
    bank_ac = db.Column(db.String(18))
    bank_ifsc = db.Column(db.String(11))

    image = db.Column(db.String(50), default="")

    # Invoices reference
    invoices = db.relationship(
        "Invoice", backref="customer", cascade="all, delete-orphan"
    )

    # Use utc to ensure timezone-independent creation timestamp
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Serialization for API responses
    def to_dict(self):
        """
        Converts the Customer object into a dictionary suitable for JSON responses.

        Returns
        -------
        dict
            Dictionary containing customer data
        """
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "email": self.email,
            "phone": self.phone,
            "gst": self.gst,
            "adhaar": self.address,
            "pan": self.pan,
            "bank_ac": self.bank_ac,
            "bank_ifsc": self.bank_ifsc,
            "image": self.image,
            "created_at": self.created_at,
            "invoices": [invoice.to_dict() for invoice in self.invoices]
        }

from extensions import db
from datetime import datetime, timezone


class Product(db.Model):
    """
    Product model for the ERP system.

    Represents each item stored in inventory along with pricing,
    tax information, stock levels, and meta-identification details.

    Columns
    -------
        id (int): Unique product ID (Primary Key).

        name (str): Product name.
        description (str): Optional long text describing the product.

        buy_price (float): Purchase price of the product.
        sell_price (float): Selling price used for billing.
        mrp (float): Maximum Retail Price.

        hsn_code (str): HSN code used for GST classification.
        gst (str): GST percentage or category (e.g., "18%", "12%").

        quantity (int): Number of units currently in stock.
        unit (str): Unit of measurement (e.g., pcs, box, kg).

        brand (str): Product brand.
        model (str): Product model number or identifier.

        image (str): Path or filename of the product image.

        created_at (datetime): Timestamp when the product was added.

    Methods
    -------
        to_dict()
            Serializes the Product object into a dictionary suitable for JSON
            API responses. Useful for returning product details to the frontend.
    """

    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)

    # Basic details
    name = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text)

    # Pricing
    buy_price = db.Column(db.Float, nullable=False)
    sell_price = db.Column(db.Float, nullable=False)
    mrp = db.Column(db.Float)

    # GST
    hsn_code = db.Column(db.String(10))
    gst = db.Column(db.Float)

    # Stock
    quantity = db.Column(db.Integer, default=0)

    # Meta
    unit = db.Column(db.String(20), default="pcs")
    brand = db.Column(db.String(50))
    model = db.Column(db.String(50))
    image = db.Column(db.String(100), default="")

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """
        Converts the Product object into a dictionary suitable for JSON responses.

        Returns
        -------
        dict
            Dictionary containing product data
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "mrp": self.mrp,
            "hsn_code": self.hsn_code,
            "gst": self.gst,
            "quantity": self.quantity,
            "unit": self.unit,
            "brand": self.brand,
            "model": self.model,
            "image": self.image,
            "created_at": self.created_at,
        }

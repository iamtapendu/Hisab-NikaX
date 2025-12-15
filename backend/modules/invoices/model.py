from flask import abort
from backend.dependecies.extensions import db
from sqlalchemy import select
from products.model import Product
from datetime import datetime, timezone


class Invoice(db.Model):
    """
    Invoice model for the ERP system.

    Represents the invoice header containing customer details,
    billing amounts, tax information, and invoice metadata.

    Fields
    ------
        id (int): Unique invoice ID (Primary Key).

        customer_id (int): Foreign key referencing the customer.

        subtotal (float): Total before discount.
        discount (float): Optional discount amount.
        total (float): Final amount payable after discount.
        paid_amount (float): Amount which customer pays.

        payment_status (str): Payment state ("paid", "pending", "partial").
        notes (str): Optional remarks for the invoice.

        created_at (datetime): Timestamp when invoice was created.

    Relationships
    -------------
        customer: Linked Customer object.
        items: List of line items in InvoiceItem table.

    Methods
    -------
    to_dict()
        Serializes the Invoice object into a dictionary suitable for JSON
        API responses. Useful for returning invoice details to the frontend.
    """

    __tablename__ = "invoices"

    id = db.Column(db.Integer, primary_key=True)

    # Customer reference
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)

    # InvoiceItems reference
    items = db.relationship(
        "InvoiceItem", backref="invoice", cascade="all, delete-orphan"
    )

    # Amounts
    subtotal = db.Column(db.Float, default=0.0)
    discount = db.Column(db.Float, default=0.0)
    total = db.Column(db.Float, default=0.0)
    paid_amount = db.Column(db.Float, default=0.0)

    payment_status = db.Column(db.String(20), default="pending")
    notes = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """
        Converts the Invoice object into a dictionary suitable for JSON responses.

        Returns
        -------
        dict
            Dictionary containing invoice data
        """
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "subtotal": self.subtotal,
            "discount": self.discount,
            "paid_amount": self.paid_amount,
            "total": self.total,
            "payment_status": self.payment_status,
            "notes": self.notes,
            "created_at": self.created_at,
            "items": [item.to_dict() for item in self.items],
        }


class InvoiceItem(db.Model):
    """
    Sales (Invoice Line Item) model for ERP.

    Represents a single product entry in an invoice, including
    quantity sold, unit price, GST rate, and total line amount.

    Fields
    ------
        id (int): Unique line item ID.

        invoice_id (int): Foreign key referencing invoice header.
        product_id (int): Foreign key referencing product master.

        quantity (int): Units sold of the product.
        unit_price (float): Selling price per unit.
        line_total (float): Total cost including GST.

        created_at (datetime): Timestamp when item was added.

    Relationships
    -------------
        product: Linked product object.

    Methods
    -------
    __init__(product_id, quantity=1, unit_price=None)
        Initializes a new InvoiceItem instance and derives default pricing
        from the Product table when a unit price is not supplied.

    to_dict()
        Serializes the InvoiceItem object into a dictionary suitable for JSON
        API responses. Useful for returning invoice item details to the frontend.

    """

    __tablename__ = "invoice_items"

    id = db.Column(db.Integer, primary_key=True)

    invoice_id = db.Column(db.Integer, db.ForeignKey("invoices.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    product = db.relationship("Product")

    quantity = db.Column(db.Integer, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    line_total = db.Column(db.Float, default=0.0)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __init__(self, invoice_id, product_id, quantity=1, unit_price=None):
        """
        Initialize an InvoiceItem instance.

        Parameters
        ----------
        invoice_id : int
            ID of the invoice. Used as parent for InvoiceItems.

        product_id : int
            ID of the product being added to the invoice. Used to fetch
            default pricing when unit_price is not provided.

        quantity : int, optional
            Number of units being sold. Defaults to 1.

        unit_price : float, optional
            Explicit selling price per unit. If omitted (None), the model
            automatically fetches the product's default sell_price from the
            Product table.

        Raises
        ------
        404 Not Found
            If the supplied product_id does not match any product record in the database.
        """
        super().__init__()

        self.invoice_id = invoice_id
        self.product_id = product_id
        self.quantity = quantity

        if unit_price is None:
            product = db.session.execute(
                select(Product).where(Product.id == product_id)
            ).scalar_one_or_none()

            if product is None:
                abort(404, description=f"Product with id {product_id} not found.")

            self.unit_price = product.sell_price
        else:
            self.unit_price = unit_price

        self.line_total = self.quantity * self.unit_price

    def to_dict(self):
        """
        Converts the InvoiceItem object into a dictionary suitable for JSON responses.

        Returns
        -------
        dict
            Dictionary containing product data
        """
        return {
            "id": self.id,
            "invoice_id": self.invoice_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "line_total": self.line_total,
            "created_at": self.created_at,
            "product": {
                "name": self.product.name,
                "brand": self.product.brand,
                "model": self.product.model,
                "unit": self.product.unit,
                "mrp": self.product.mrp,
            },
        }

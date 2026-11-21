
from app import db
from datetime import datetime


class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)

    purchase_price = db.Column(
        db.Numeric(10, 2), nullable=False, default=0
    )
    sale_price = db.Column(
        db.Numeric(10, 2), nullable=False, default=0
    )

    stock = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock = db.Column(db.Integer, nullable=False, default=5)

    expiration_date = db.Column(db.Date, nullable=True)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=datetime.now)

    category = db.relationship(
        "Category",
        back_populates="products"
    )

    movements = db.relationship(
        "InventoryMovement",
        back_populates="product",
        lazy=True,
        passive_deletes=True
    )

    def __repr__(self):
        return f"<Product {self.name}>"

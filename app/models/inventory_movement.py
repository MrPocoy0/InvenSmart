from app import db


class InventoryMovement(db.Model):
    __tablename__ = "inventory_movements"

    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="ck_inventory_movement_quantity_positive"),
        db.CheckConstraint(
            "movement_type IN ('entry', 'exit')",
            name="ck_inventory_movement_type_valid"
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", ondelete="RESTRICT"),
        nullable=False,
        index=True
    )
    movement_type = db.Column(db.String(10), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    stock_before = db.Column(db.Integer, nullable=False)
    stock_after = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.current_timestamp()
    )

    product = db.relationship("Product", back_populates="movements")

    def __repr__(self):
        return f"<InventoryMovement {self.movement_type} {self.quantity}>"

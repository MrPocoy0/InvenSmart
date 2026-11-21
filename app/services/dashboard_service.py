from sqlalchemy import func

from app import db
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product


def get_dashboard_data(alerts):
    total_units = db.session.query(
        func.coalesce(func.sum(Product.stock), 0)
    ).scalar()
    low_stock = alerts["low_stock"]
    out_of_stock = alerts["out_of_stock"]
    expired = alerts["expired"]
    upcoming = alerts["upcoming"]

    latest_movements = (
        InventoryMovement.query
        .join(Product)
        .order_by(InventoryMovement.created_at.desc())
        .limit(5)
        .all()
    )

    return {
        "total_products": Product.query.count(),
        "total_units": int(total_units or 0),
        "low_stock_count": len(low_stock),
        "out_of_stock_count": len(out_of_stock),
        "expired_count": len(expired),
        "upcoming_count": len(upcoming),
        "latest_movements": latest_movements,
    }

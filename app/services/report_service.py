from datetime import date, datetime

from sqlalchemy import func

from app import db
from app.models.category import Category
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product


def parse_report_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        return None


def get_inventory_report(start_date=None, end_date=None, category_id=None):
    product_query = Product.query
    if category_id:
        product_query = product_query.filter(Product.category_id == category_id)
    products = product_query.order_by(Product.name.asc()).all()
    product_ids = [product.id for product in products]
    alerts = {
        "low_stock": [p for p in products if p.stock > 0 and p.stock <= p.minimum_stock],
        "out_of_stock": [p for p in products if p.stock == 0],
        "expired": [p for p in products if p.expiration_date and p.expiration_date < date.today()],
    }
    movement_query = InventoryMovement.query.join(Product)
    if product_ids:
        movement_query = movement_query.filter(InventoryMovement.product_id.in_(product_ids))
    else:
        movement_query = movement_query.filter(InventoryMovement.id == -1)
    if start_date:
        movement_query = movement_query.filter(InventoryMovement.created_at >= start_date)
    if end_date:
        movement_query = movement_query.filter(InventoryMovement.created_at < datetime.combine(end_date, datetime.max.time()))
    movements = movement_query.order_by(InventoryMovement.created_at.desc()).all()
    entries = sum(m.quantity for m in movements if m.movement_type == "entry")
    exits = sum(m.quantity for m in movements if m.movement_type == "exit")
    category_query = db.session.query(Category.name, func.count(Product.id), func.coalesce(func.sum(Product.stock), 0)).outerjoin(Category.products)
    if category_id:
        category_query = category_query.filter(Category.id == category_id)
    category_rows = category_query.group_by(Category.id, Category.name).order_by(Category.name).all()
    movement_chart = {}
    for movement in movements:
        movement_date = movement.created_at.date().isoformat() if movement.created_at else "Sin fecha"
        row = movement_chart.setdefault(movement_date, {"date": movement_date, "entries": 0, "exits": 0})
        row["entries" if movement.movement_type == "entry" else "exits"] += movement.quantity
    return {
        "products": products, "movements": movements, "alerts": alerts,
        "total_products": len(products), "total_units": sum(p.stock for p in products),
        "entries": entries, "exits": exits, "categories": category_rows,
        "movement_chart": list(reversed(list(movement_chart.values()))),
        "start_date": start_date, "end_date": end_date, "category_id": category_id,
    }

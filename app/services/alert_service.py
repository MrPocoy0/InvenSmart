from datetime import date, timedelta

from app.models.product import Product


def get_inventory_alerts(days=30):
    today = date.today()
    limit_date = today + timedelta(days=days)
    products = Product.query.order_by(Product.name.asc()).all()

    return {
        "low_stock": [
            product for product in products
            if product.stock > 0 and product.stock <= product.minimum_stock
        ],
        "out_of_stock": [product for product in products if product.stock == 0],
        "expired": [
            product for product in products
            if product.expiration_date and product.expiration_date < today
        ],
        "upcoming": [
            product for product in products
            if product.expiration_date
            and today <= product.expiration_date <= limit_date
        ],
        "today": today,
        "limit_date": limit_date,
    }


def detect_inventory_alerts(days=30):
    """Ejecuta la detección automática de alertas sin escribir en la base."""
    return get_inventory_alerts(days=days)

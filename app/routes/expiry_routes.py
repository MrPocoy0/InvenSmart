
from datetime import date, timedelta

from flask import Blueprint, render_template

from app.models.product import Product


expiry_bp = Blueprint(
    "expiry",
    __name__,
    url_prefix="/vencimientos"
)


@expiry_bp.route("/")
def list_expirations():
    today = date.today()
    limit_date = today + timedelta(days=30)

    # Productos cuya fecha de vencimiento ya pasó
    expired_products = (
        Product.query
        .filter(Product.expiration_date < today)
        .order_by(Product.expiration_date.asc())
        .all()
    )

    # Productos que vencerán dentro de los próximos 30 días
    upcoming_products = (
        Product.query
        .filter(
            Product.expiration_date >= today,
            Product.expiration_date <= limit_date
        )
        .order_by(Product.expiration_date.asc())
        .all()
    )

    return render_template(
        "expirations.html",
        expired_products=expired_products,
        upcoming_products=upcoming_products,
        today=today
    )

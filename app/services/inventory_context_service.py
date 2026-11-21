"""Construcción de un contexto reducido y de solo lectura para la IA."""

from app.services.alert_service import get_inventory_alerts
from app.services.dashboard_service import get_dashboard_data


def build_inventory_context():
    alerts = get_inventory_alerts()
    dashboard = get_dashboard_data(alerts)
    return {
        "metrics": {
            "total_products": dashboard["total_products"],
            "total_units": dashboard["total_units"],
            "low_stock": dashboard["low_stock_count"],
            "out_of_stock": dashboard["out_of_stock_count"],
            "expired": dashboard["expired_count"],
            "upcoming_expiry": dashboard["upcoming_count"],
        },
        "alerts": {
            "low_stock": [_product_summary(p) for p in alerts["low_stock"]],
            "out_of_stock": [_product_summary(p) for p in alerts["out_of_stock"]],
            "expired": [_product_summary(p) for p in alerts["expired"]],
            "upcoming": [_product_summary(p) for p in alerts["upcoming"]],
        },
        "latest_movements": [
            {
                "product": movement.product.name,
                "type": movement.movement_type,
                "quantity": movement.quantity,
                "created_at": movement.created_at.isoformat() if movement.created_at else None,
            }
            for movement in dashboard["latest_movements"]
        ],
    }


def _product_summary(product):
    return {
        "name": product.name,
        "stock": product.stock,
        "minimum_stock": product.minimum_stock,
        "expiration_date": product.expiration_date.isoformat() if product.expiration_date else None,
    }

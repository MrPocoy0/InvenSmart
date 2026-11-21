from datetime import date, timedelta

from app import db
from app.models.category import Category
from app.models.product import Product
from app.services.alert_service import get_inventory_alerts
from app.services.dashboard_service import get_dashboard_data
from app.services.inventory_service import register_movement


def _add_product(name, code, stock, minimum_stock, expiration_date=None):
    category = Category.query.first()
    product = Product(
        name=name,
        code=code,
        stock=stock,
        minimum_stock=minimum_stock,
        purchase_price=1,
        sale_price=2,
        expiration_date=expiration_date,
        category=category,
    )
    db.session.add(product)
    db.session.commit()
    return product


def test_dashboard_indicators_use_real_inventory(client, app, product):
    with app.app_context():
        _add_product("Agotado", "DASH-001", 0, 2)
        register_movement(product, "entry", 3, "Dashboard")
        response = client.get("/")
        body = response.get_data(as_text=True)
        assert response.status_code == 200
        assert "2" in body
        assert "13" in body


def test_alert_service_detects_stock_and_expiration_alerts(app, product):
    with app.app_context():
        _add_product("Bajo", "ALT-001", 1, 2)
        _add_product("Vencido", "ALT-002", 4, 2, date.today() - timedelta(days=1))
        _add_product("Próximo", "ALT-003", 4, 2, date.today() + timedelta(days=5))
        alerts = get_inventory_alerts()
        assert any(item.code == "ALT-001" for item in alerts["low_stock"])
        assert any(item.code == "ALT-002" for item in alerts["expired"])
        assert any(item.code == "ALT-003" for item in alerts["upcoming"])


def test_alerts_screen_displays_real_alerts(client, app, product):
    with app.app_context():
        _add_product("Alerta visible", "ALT-004", 0, 2)
    response = client.get("/alertas/")
    assert response.status_code == 200
    assert "Alerta visible" in response.get_data(as_text=True)


def test_dashboard_includes_latest_movement(app, product):
    with app.app_context():
        register_movement(product, "entry", 2, "Último movimiento")
        data = get_dashboard_data(get_inventory_alerts())
        assert len(data["latest_movements"]) == 1
        assert data["latest_movements"][0].description == "Último movimiento"

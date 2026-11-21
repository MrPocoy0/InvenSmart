from datetime import date, timedelta

from app import db
from app.models.category import Category
from app.models.product import Product
from app.services.inventory_service import register_movement


def seed_report_data(app):
    with app.app_context():
        category = Category(name="Reportes")
        product = Product(code="REP-001", name="Producto reporte", stock=2, minimum_stock=5, category=category, expiration_date=date.today() - timedelta(days=1))
        db.session.add(product)
        db.session.commit()
        register_movement(product.id, "entry", 3, "Ingreso prueba")
        register_movement(product.id, "exit", 1, "Salida prueba")


def test_report_page_uses_real_indicators(client, app):
    seed_report_data(app)
    response = client.get("/reportes/")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Producto reporte" in body
    assert "Movimientos de inventario" in body
    assert "Entradas" in body
    assert "Entradas y salidas" in body
    assert "Distribución por categoría" in body


def test_report_filters_by_category_and_dates(client, app):
    seed_report_data(app)
    response = client.get("/reportes/?category_id=999&start_date=2030-01-01")
    assert response.status_code == 200
    assert "Producto reporte" not in response.get_data(as_text=True)


def test_report_csv_respects_filters(client, app):
    seed_report_data(app)
    response = client.get("/reportes/exportar.csv")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert response.mimetype == "text/csv"
    assert "Producto reporte" in body
    assert "Ingreso prueba" in body
    assert "Stock anterior" in body


def test_report_empty_period_shows_empty_states(client, app):
    seed_report_data(app)
    response = client.get("/reportes/?start_date=2030-01-01&end_date=2030-01-02")
    body = response.get_data(as_text=True)
    assert "No hay movimientos en el periodo seleccionado" in body

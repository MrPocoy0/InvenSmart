from app import db
from app.models.product import Product
from app.services.inventory_service import register_movement


def test_product_edit_does_not_change_stock_from_post(app, product):
    with app.app_context():
        response = app.test_client().post(
            f"/productos/editar/{product}",
            data={
                "code": "TEST-001",
                "name": "Producto editado",
                "purchase_price": "1",
                "sale_price": "2",
                "stock": "999",
                "minimum_stock": "2",
                "category_id": "1",
                "expiration_date": "",
                "description": "",
            },
        )
        assert response.status_code == 302
        assert db.session.get(Product, product).stock == 10


def test_product_with_movements_cannot_be_deleted(app, product):
    with app.app_context():
        register_movement(product, "entry", 2, "Trazabilidad")
        response = app.test_client().post(f"/productos/eliminar/{product}")
        assert response.status_code == 302
        assert db.session.get(Product, product) is not None

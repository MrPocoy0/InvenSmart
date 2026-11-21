from app import db
from app.models.category import Category
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.services.inventory_service import register_movement


def _second_product():
    category = Category(name="Otra categoría")
    product = Product(
        code="TEST-002",
        name="Segundo producto",
        stock=3,
        minimum_stock=1,
        purchase_price=2,
        sale_price=4,
        category=category,
    )
    db.session.add(product)
    db.session.commit()
    return product


def test_history_is_visible(client, app, product):
    with app.app_context():
        register_movement(product, "entry", 2, "Recepción")
    response = client.get("/movimientos/")
    assert response.status_code == 200
    assert "Recepción" in response.get_data(as_text=True)
    assert "Stock anterior" in response.get_data(as_text=True)
    assert "Stock posterior" in response.get_data(as_text=True)


def test_history_filters_by_product(client, app, product):
    with app.app_context():
        other = _second_product()
        register_movement(product, "entry", 1, "Producto uno")
        register_movement(other.id, "entry", 1, "Producto dos")
    response = client.get(f"/movimientos/?product_id={product}")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Producto uno" in body
    assert "Producto dos" not in body


def test_history_filters_by_movement_type(client, app, product):
    with app.app_context():
        register_movement(product, "entry", 2, "Entrada visible")
        register_movement(product, "exit", 1, "Salida visible")
    response = client.get("/movimientos/?movement_type=exit")
    body = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Salida visible" in body
    assert "Entrada visible" not in body


def test_new_movement_form_is_available(client):
    response = client.get("/movimientos/nuevo")
    assert response.status_code == 200
    assert "Registrar movimiento" in response.get_data(as_text=True)


def test_entry_post_updates_stock_and_history(client, app, product):
    response = client.post(
        "/movimientos/nuevo",
        data={
            "product_id": str(product),
            "movement_type": "entry",
            "quantity": "4",
            "description": "Entrada por compra",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        saved = db.session.get(Product, product)
        movement = InventoryMovement.query.one()
        assert saved.stock == 14
        assert movement.stock_before == 10
        assert movement.stock_after == 14
        assert movement.description == "Entrada por compra"


def test_exit_post_updates_stock_and_history(client, app, product):
    response = client.post(
        "/movimientos/nuevo",
        data={
            "product_id": str(product),
            "movement_type": "exit",
            "quantity": "4",
            "description": "Salida por venta",
        },
    )
    assert response.status_code == 302
    with app.app_context():
        saved = db.session.get(Product, product)
        movement = InventoryMovement.query.one()
        assert saved.stock == 6
        assert movement.stock_before == 10
        assert movement.stock_after == 6


def test_invalid_quantity_is_rejected_by_route(client, app, product):
    response = client.post(
        "/movimientos/nuevo",
        data={
            "product_id": str(product),
            "movement_type": "entry",
            "quantity": "0",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert InventoryMovement.query.count() == 0
        assert db.session.get(Product, product).stock == 10


def test_exit_above_stock_is_rejected_by_route(client, app, product):
    response = client.post(
        "/movimientos/nuevo",
        data={
            "product_id": str(product),
            "movement_type": "exit",
            "quantity": "11",
        },
    )
    assert response.status_code == 200
    with app.app_context():
        assert InventoryMovement.query.count() == 0
        assert db.session.get(Product, product).stock == 10


def test_route_persists_stock_and_history_together(client, app, product):
    client.post(
        "/movimientos/nuevo",
        data={
            "product_id": str(product),
            "movement_type": "entry",
            "quantity": "7",
            "description": "Reposición completa",
        },
    )
    with app.app_context():
        movement = InventoryMovement.query.one()
        saved = db.session.get(Product, product)
        assert saved.stock == movement.stock_after
        assert movement.stock_before + movement.quantity == movement.stock_after

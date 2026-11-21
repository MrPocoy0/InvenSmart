import pytest

from app import db
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.services.inventory_service import register_movement


def test_entry_updates_stock_and_traceability(app, product):
    with app.app_context():
        movement = register_movement(product, "entry", 5, "Reposición")
        saved_product = db.session.get(Product, product)
        assert saved_product.stock == 15
        assert movement.stock_before == 10
        assert movement.stock_after == 15


def test_exit_updates_stock_and_traceability(app, product):
    with app.app_context():
        movement = register_movement(product, "exit", 4, "Venta")
        saved_product = db.session.get(Product, product)
        assert saved_product.stock == 6
        assert movement.stock_before == 10
        assert movement.stock_after == 6


@pytest.mark.parametrize("quantity", [0, -1])
def test_invalid_quantity_is_rejected(app, product, quantity):
    with app.app_context():
        with pytest.raises(ValueError):
            register_movement(product, "entry", quantity)
        assert db.session.query(InventoryMovement).count() == 0
        assert db.session.get(Product, product).stock == 10


def test_exit_cannot_exceed_stock(app, product):
    with app.app_context():
        with pytest.raises(ValueError):
            register_movement(product, "exit", 11)
        assert db.session.query(InventoryMovement).count() == 0
        assert db.session.get(Product, product).stock == 10


def test_stock_and_history_rollback_together(app, product, monkeypatch):
    with app.app_context():
        original_commit = db.session.commit

        def failing_commit():
            raise RuntimeError("commit failure")

        monkeypatch.setattr(db.session, "commit", failing_commit)
        with pytest.raises(RuntimeError):
            register_movement(product, "entry", 3)
        monkeypatch.setattr(db.session, "commit", original_commit)
        assert db.session.query(InventoryMovement).count() == 0
        assert db.session.get(Product, product).stock == 10

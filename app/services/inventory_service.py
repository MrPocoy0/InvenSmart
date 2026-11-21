from app import db
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product


MOVEMENT_TYPES = {"entry", "exit"}


def register_movement(product_id, movement_type, quantity, description=None):
    if movement_type not in MOVEMENT_TYPES:
        raise ValueError("El tipo de movimiento no es válido.")
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("La cantidad debe ser mayor que cero.")

    product = db.session.get(Product, product_id, with_for_update=True)
    if product is None:
        raise ValueError("El producto no existe.")
    if movement_type == "exit" and quantity > product.stock:
        raise ValueError("La salida no puede superar el stock disponible.")

    stock_before = product.stock
    stock_after = (
        stock_before + quantity
        if movement_type == "entry"
        else stock_before - quantity
    )
    if stock_after < 0:
        raise ValueError("El stock resultante no puede ser negativo.")

    movement = InventoryMovement(
        product=product,
        movement_type=movement_type,
        quantity=quantity,
        stock_before=stock_before,
        stock_after=stock_after,
        description=description or None
    )
    product.stock = stock_after
    db.session.add(movement)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return movement

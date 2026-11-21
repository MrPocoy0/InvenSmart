from flask import Blueprint, flash, redirect, render_template, request, url_for

from app import db
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.services.inventory_service import register_movement


movement_bp = Blueprint("movement", __name__, url_prefix="/movimientos")


@movement_bp.route("/")
def list_movements():
    product_id = request.args.get("product_id", type=int)
    movement_type = request.args.get("movement_type", "").strip()
    query = InventoryMovement.query.join(Product)
    if product_id:
        query = query.filter(InventoryMovement.product_id == product_id)
    if movement_type in {"entry", "exit"}:
        query = query.filter(InventoryMovement.movement_type == movement_type)
    movements = query.order_by(InventoryMovement.created_at.desc()).all()
    products = Product.query.order_by(Product.name.asc()).all()
    return render_template(
        "movements.html", movements=movements, products=products,
        selected_product_id=product_id, selected_movement_type=movement_type
    )


@movement_bp.route("/nuevo", methods=["GET", "POST"])
def create_movement():
    products = Product.query.order_by(Product.name.asc()).all()
    if request.method == "POST":
        try:
            product_id = int(request.form.get("product_id", "0"))
            movement_type = request.form.get("movement_type", "").strip()
            quantity = int(request.form.get("quantity", "0"))
            description = request.form.get("description", "").strip()
            register_movement(product_id, movement_type, quantity, description)
            flash("Movimiento registrado y stock actualizado correctamente.", "success")
            return redirect(url_for("movement.list_movements"))
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
        except Exception:
            db.session.rollback()
            flash("No se pudo registrar el movimiento. Verifica los datos e inténtalo nuevamente.", "danger")
    return render_template("movement_form.html", products=products, page_title="Registrar movimiento")

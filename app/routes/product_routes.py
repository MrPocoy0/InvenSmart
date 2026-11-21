
from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from sqlalchemy import or_

from app import db
from app.models.product import Product
from app.models.category import Category
from app.models.inventory_movement import InventoryMovement


product_bp = Blueprint(
    "product",
    __name__,
    url_prefix="/productos"
)


# =========================================
# LISTAR Y BUSCAR PRODUCTOS
# =========================================

@product_bp.route("/")
def list_products():
    search = request.args.get("q", "").strip()

    query = Product.query

    if search:
        query = query.filter(
            or_(
                Product.code.ilike(f"%{search}%"),
                Product.name.ilike(f"%{search}%")
            )
        )

    products = query.order_by(Product.name.asc()).all()

    return render_template(
        "products.html",
        products=products,
        search=search
    )


# =========================================
# REGISTRAR PRODUCTO
# =========================================

@product_bp.route("/nuevo", methods=["GET", "POST"])
def create_product():
    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == "POST":
        try:
            code = request.form.get("code", "").strip()
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()

            purchase_price = Decimal(
                request.form.get("purchase_price", "0")
            )
            sale_price = Decimal(
                request.form.get("sale_price", "0")
            )

            stock = int(request.form.get("stock", "0"))
            minimum_stock = int(
                request.form.get("minimum_stock", "5")
            )

            category_id = int(request.form.get("category_id", "0"))

            expiration_value = request.form.get(
                "expiration_date", ""
            )

            expiration_date = (
                datetime.strptime(
                    expiration_value, "%Y-%m-%d"
                ).date()
                if expiration_value
                else None
            )

            if not code or not name:
                raise ValueError(
                    "El código y el nombre son obligatorios."
                )

            if purchase_price < 0 or sale_price < 0:
                raise ValueError(
                    "Los precios no pueden ser negativos."
                )

            if stock < 0 or minimum_stock < 0:
                raise ValueError("El stock no puede ser negativo.")

            category = db.session.get(Category, category_id)

            if not category:
                raise ValueError(
                    "Selecciona una categoría válida."
                )

            existing_product = Product.query.filter_by(
                code=code
            ).first()

            if existing_product:
                raise ValueError(
                    "Ya existe un producto con ese código."
                )

            product = Product(
                code=code,
                name=name,
                description=description or None,
                purchase_price=purchase_price,
                sale_price=sale_price,
                stock=stock,
                minimum_stock=minimum_stock,
                expiration_date=expiration_date,
                category_id=category_id
            )

            db.session.add(product)
            db.session.commit()

            flash(
                "Producto registrado correctamente.",
                "success"
            )

            return redirect(url_for("product.list_products"))

        except (ValueError, InvalidOperation) as error:
            db.session.rollback()
            flash(str(error), "danger")

        except Exception:
            db.session.rollback()
            flash(
                "No se pudo registrar el producto. "
                "Verifica los datos e inténtalo nuevamente.",
                "danger"
            )

    return render_template(
        "product_form.html",
        product=None,
        categories=categories,
        page_title="Registrar producto"
    )


# =========================================
# EDITAR PRODUCTO
# =========================================

@product_bp.route(
    "/editar/<int:product_id>",
    methods=["GET", "POST"]
)
def edit_product(product_id):
    product = db.get_or_404(Product, product_id)

    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == "POST":
        try:
            code = request.form.get("code", "").strip()
            name = request.form.get("name", "").strip()
            description = request.form.get("description", "").strip()

            purchase_price = Decimal(
                request.form.get("purchase_price", "0")
            )
            sale_price = Decimal(
                request.form.get("sale_price", "0")
            )

            minimum_stock = int(
                request.form.get("minimum_stock", "5")
            )

            category_id = int(request.form.get("category_id", "0"))

            expiration_value = request.form.get(
                "expiration_date", ""
            )

            expiration_date = (
                datetime.strptime(
                    expiration_value, "%Y-%m-%d"
                ).date()
                if expiration_value
                else None
            )

            if not code or not name:
                raise ValueError(
                    "El código y el nombre son obligatorios."
                )

            if purchase_price < 0 or sale_price < 0:
                raise ValueError(
                    "Los precios no pueden ser negativos."
                )

            if minimum_stock < 0:
                raise ValueError("El stock mínimo no puede ser negativo.")

            category = db.session.get(Category, category_id)

            if not category:
                raise ValueError(
                    "Selecciona una categoría válida."
                )

            existing_product = Product.query.filter(
                Product.code == code,
                Product.id != product.id
            ).first()

            if existing_product:
                raise ValueError(
                    "Otro producto ya utiliza ese código."
                )

            product.code = code
            product.name = name
            product.description = description or None
            product.purchase_price = purchase_price
            product.sale_price = sale_price
            product.minimum_stock = minimum_stock
            product.expiration_date = expiration_date
            product.category_id = category_id

            db.session.commit()

            flash(
                "Producto actualizado correctamente.",
                "success"
            )

            return redirect(url_for("product.list_products"))

        except (ValueError, InvalidOperation) as error:
            db.session.rollback()
            flash(str(error), "danger")

        except Exception:
            db.session.rollback()
            flash(
                "No se pudo actualizar el producto. "
                "Verifica los datos e inténtalo nuevamente.",
                "danger"
            )

    return render_template(
        "product_form.html",
        product=product,
        categories=categories,
        page_title="Editar producto"
    )


# =========================================
# ELIMINAR PRODUCTO
# =========================================

@product_bp.route(
    "/eliminar/<int:product_id>",
    methods=["POST"]
)
def delete_product(product_id):
    product = db.get_or_404(Product, product_id)

    if InventoryMovement.query.filter_by(product_id=product.id).first():
        flash(
            "No se puede eliminar: el producto tiene movimientos registrados.",
            "danger"
        )
        return redirect(url_for("product.list_products"))

    try:
        db.session.delete(product)
        db.session.commit()

        flash(
            "Producto eliminado correctamente.",
            "success"
        )

    except Exception:
        db.session.rollback()
        flash(
            "No se pudo eliminar el producto.",
            "danger"
        )

    return redirect(url_for("product.list_products"))

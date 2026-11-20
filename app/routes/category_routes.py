
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db
from app.models.category import Category

category_bp = Blueprint(
    "category",
    __name__,
    url_prefix="/categorias"
)


# LISTAR CATEGORÍAS
@category_bp.route("/")
def list_categories():
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template(
        "categories.html",
        categories=categories
    )


# REGISTRAR CATEGORÍA
@category_bp.route("/crear", methods=["POST"])
def create_category():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("El nombre de la categoría es obligatorio.", "error")
        return redirect(url_for("category.list_categories"))

    existing = Category.query.filter_by(name=name).first()

    if existing:
        flash("Esta categoría ya está registrada.", "error")
        return redirect(url_for("category.list_categories"))

    category = Category(
        name=name,
        description=description if description else None
    )

    db.session.add(category)
    db.session.commit()

    flash("Categoría registrada correctamente.", "success")
    return redirect(url_for("category.list_categories"))


# EDITAR CATEGORÍA
@category_bp.route("/editar/<int:category_id>", methods=["POST"])
def edit_category(category_id):
    category = db.session.get(Category, category_id)

    if category is None:
        flash("La categoría no existe.", "error")
        return redirect(url_for("category.list_categories"))

    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()

    if not name:
        flash("El nombre de la categoría es obligatorio.", "error")
        return redirect(url_for("category.list_categories"))

    existing = Category.query.filter(
        Category.name == name,
        Category.id != category_id
    ).first()

    if existing:
        flash("Ya existe otra categoría con ese nombre.", "error")
        return redirect(url_for("category.list_categories"))

    category.name = name
    category.description = description if description else None

    db.session.commit()

    flash("Categoría actualizada correctamente.", "success")
    return redirect(url_for("category.list_categories"))


# ELIMINAR CATEGORÍA
@category_bp.route("/eliminar/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    category = db.session.get(Category, category_id)

    if category is None:
        flash("La categoría no existe.", "error")
        return redirect(url_for("category.list_categories"))

    if category.products:
        flash(
            "No se puede eliminar: esta categoría tiene productos asociados.",
            "error"
        )
        return redirect(url_for("category.list_categories"))

    db.session.delete(category)
    db.session.commit()

    flash("Categoría eliminada correctamente.", "success")
    return redirect(url_for("category.list_categories"))

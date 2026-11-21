import csv
from io import StringIO

from flask import Blueprint, Response, render_template, request

from app.models.category import Category
from app.services.report_service import get_inventory_report, parse_report_date

report_bp = Blueprint("report", __name__, url_prefix="/reportes")


def _filters():
    return parse_report_date(request.args.get("start_date")), parse_report_date(request.args.get("end_date")), request.args.get("category_id", type=int)


@report_bp.route("/")
def index():
    start_date, end_date, category_id = _filters()
    report = get_inventory_report(start_date, end_date, category_id)
    return render_template("reports.html", report=report, categories=Category.query.order_by(Category.name).all(), filter_start=request.args.get("start_date", ""), filter_end=request.args.get("end_date", ""))


@report_bp.route("/exportar.csv")
def export_csv():
    start_date, end_date, category_id = _filters()
    report = get_inventory_report(start_date, end_date, category_id)
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Fecha", "Producto", "Código", "Tipo", "Cantidad", "Stock anterior", "Stock posterior", "Descripción"])
    for movement in report["movements"]:
        writer.writerow([movement.created_at.strftime("%Y-%m-%d %H:%M") if movement.created_at else "", movement.product.name, movement.product.code, movement.movement_type, movement.quantity, movement.stock_before, movement.stock_after, movement.description or ""])
    return Response("\ufeff" + output.getvalue(), mimetype="text/csv", headers={"Content-Disposition": "attachment; filename=invensmart_reporte_movimientos.csv"})

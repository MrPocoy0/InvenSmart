from flask import Blueprint, render_template

from app.services.alert_service import get_inventory_alerts


alert_bp = Blueprint("alert", __name__, url_prefix="/alertas")


@alert_bp.route("/")
def list_alerts():
    alerts = get_inventory_alerts()
    return render_template("alerts.html", alerts=alerts)


from flask import Blueprint, render_template

from app.services.alert_service import detect_inventory_alerts
from app.services.dashboard_service import get_dashboard_data

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    alerts = detect_inventory_alerts()
    dashboard = get_dashboard_data(alerts)
    return render_template("dashboard.html", alerts=alerts, **dashboard)

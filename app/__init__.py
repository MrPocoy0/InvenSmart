
import os
from urllib.parse import quote_plus

from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__)

    if test_config is None:
        load_dotenv()

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "clave-desarrollo-invensmart"
    )

    if test_config is not None:
        app.config.update(test_config)

    if app.config.get("TESTING"):
        database_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
        if not database_uri.startswith("sqlite:"):
            raise RuntimeError("Las pruebas solo pueden utilizar SQLite.")
    else:
        # Configuración de conexión con MySQL para la ejecución normal
        password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))
        app.config["SQLALCHEMY_DATABASE_URI"] = (
            f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{password}"
            f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}"
            f"/{os.getenv('MYSQL_DATABASE')}"
        )

    # Inicializar SQLAlchemy
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Registrar modelos
    from app.models.category import Category
    from app.models.product import Product
    from app.models.inventory_movement import InventoryMovement

    # Registrar rutas
    from app.routes.main_routes import main_bp
    from app.routes.category_routes import category_bp
    from app.routes.product_routes import product_bp
    from app.routes.expiry_routes import expiry_bp
    from app.routes.movement_routes import movement_bp
    from app.routes.alert_routes import alert_bp
    from app.routes.ai_routes import ai_bp
    from app.routes.report_routes import report_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(expiry_bp)
    app.register_blueprint(movement_bp)
    app.register_blueprint(alert_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(report_bp)

    @app.cli.command("check-alerts")
    def check_alerts_command():
        """Detecta alertas actuales para automatización externa (solo lectura)."""
        from click import echo
        from app.services.alert_service import detect_inventory_alerts

        alerts = detect_inventory_alerts()
        echo(
            "Alertas detectadas: "
            f"bajo={len(alerts['low_stock'])}, "
            f"agotado={len(alerts['out_of_stock'])}, "
            f"vencido={len(alerts['expired'])}, "
            f"proximo={len(alerts['upcoming'])}"
        )

    return app


import os
from urllib.parse import quote_plus

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


load_dotenv()

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Configuración de conexión con MySQL
    password = quote_plus(os.getenv("MYSQL_PASSWORD", ""))

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{password}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}"
        f"/{os.getenv('MYSQL_DATABASE')}"
    )

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "clave-desarrollo-invensmart"
    )

    # Inicializar SQLAlchemy
    db.init_app(app)

    # Registrar modelos
    from app.models.category import Category
    from app.models.product import Product

    # Registrar rutas
    from app.routes.main_routes import main_bp
    from app.routes.category_routes import category_bp
    from app.routes.product_routes import product_bp
    from app.routes.expiry_routes import expiry_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(category_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(expiry_bp)

    return app

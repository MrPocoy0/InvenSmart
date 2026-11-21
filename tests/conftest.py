import pytest

from app import db, create_app
from app.models.category import Category
from app.models.product import Product


@pytest.fixture()
def app():
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test-only-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False,
    }
    assert test_config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:")
    application = create_app(test_config)

    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def csrf_app():
    test_config = {
        "TESTING": True,
        "SECRET_KEY": "test-only-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": True,
    }
    assert test_config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:")
    application = create_app(test_config)
    with application.app_context():
        db.create_all()
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def product(app):
    with app.app_context():
        category = Category(name="Pruebas")
        product = Product(
            code="TEST-001",
            name="Producto de prueba",
            stock=10,
            minimum_stock=2,
            purchase_price=1,
            sale_price=2,
            category=category,
        )
        db.session.add(product)
        db.session.commit()
        return product.id

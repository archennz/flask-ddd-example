import pytest
from flaskr import create_app
from flaskr.db import init_db, db
from flask.testing import FlaskClient, FlaskCliRunner


@pytest.fixture()
def app():
    """Create and configure a new app instance for each test"""
    app = create_app()
    app.config.update(
        {"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"}
    )

    with app.app_context():
        init_db()

    yield app


@pytest.fixture()
def add_test_data(app):
    """Add and save test data into test db"""

    def _add_test_data(data_objects):
        with app.app_context():
            db.session.add_all(data_objects)
            db.session.commit()

    yield _add_test_data


@pytest.fixture()
def client(app) -> FlaskClient:
    """Create test client for testing"""
    return app.test_client()


@pytest.fixture()
def runner(app) -> FlaskCliRunner:
    """Create test runner for testing"""
    return app.test_cli_runner()

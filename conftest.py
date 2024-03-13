import pytest
from flaskr import create_app
from flaskr.db import init_db


# # TODO: not sure about the scope of this thing
# @pytest.fixture()
# def add_stock(session):
#     def _add_stock(lines):
#         for line in lines:
#             session.add(line)
#     yield _add_stock

@pytest.fixture()
def app():
    """Create and configure a new app instance for each test"""
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"
            }
    )

    with app.app_context():
        init_db()
        
    yield app

    # clean up 
    # should drop db on tear down

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
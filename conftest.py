import pytest
from flaskr import create_app


# TODO: not sure about the scope of this thing
@pytest.fixture()
def add_stock(session):
    def _add_stock(lines):
        for line in lines:
            session.add(line)
    yield _add_stock

@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {"TESTING": True}
    )

    # other setup can go there

    yield app

    # clean up 

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
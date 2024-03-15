from flask import Flask
from flaskr.db import db, init_db_command


def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    db.init_app(app)
    app.cli.add_command(init_db_command)

    from . import batch, allocate

    app.register_blueprint(batch.bp)
    app.register_blueprint(allocate.bp)

    return app

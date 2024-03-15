import click
from flask.cli import with_appcontext

from flask_sqlalchemy import SQLAlchemy
from flaskr.model import Base

db = SQLAlchemy(model_class=Base)


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear existing data and create new tables"""
    init_db()
    click.echo("Initialized the database.")


def init_db():
    # not sure about this
    db.drop_all()
    db.create_all()

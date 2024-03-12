import click

from flask import current_app, g
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base

engine = create_engine('sqlite:////tmp/test.db')
db_session = scoped_session(sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine))

@click.command('init-db')
def init_db():
    metadata.create_all(bind=engine)
    click.echo('Initialized the database.')

def init_app(app):
    app.cli.add_command(init_db)
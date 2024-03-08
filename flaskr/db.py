import sqlite3

from flask import current_app, g
from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine('sqlite:////tmp/test.db')
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False,
                            autoflush=False,
                            bind=engine))

def init_db():
    metadata.create_all(bind=engine)
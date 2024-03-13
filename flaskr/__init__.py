import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

from model import allocate
from .db import db, init_db_command
# db = SQLAlchemy(model_class=Base)

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)


    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    db.init_app(app)
    app.cli.add_command(init_db_command)
    
    # these are the routes
    # some random routes are working I think
    # lets make some test for this?
    from model import OrderLine, Batch

    @app.route('/batch/<batch_id>')
    def show_batch(batch_id):
        batch = db.get_or_404(Batch, batch_id)
        return batch.id

    # this is imcomplete
    @app.post('/batch')
    def add_batch():
        batch = Batch(
            ref = request.form["order_id"],
            sku = "sku",
            qty= 5
        )
        db.session.add(batch)
        db.session.commit()
        return batch.id
    

    @app.post('/allocate')
    def allocate_endpoint():
        line = OrderLine(request.form["order_id"], request.form["sku"], int(request.form["qty"]))
        stmt = select(Batch).where(Batch.sku == line.sku)
        batches = db.session.scalars(stmt)
        batch_id = allocate(line, batches)
        db.session.commit()
        return batch_id, 201
    return app

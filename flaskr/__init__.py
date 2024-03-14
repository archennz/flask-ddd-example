import os

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

from model import OutOfStock
from repository import BatchRepository
import services
from .db import db, init_db_command
from flask_pydantic import validate
import schema

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)


    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    db.init_app(app)
    app.cli.add_command(init_db_command)
    

    from model import OrderLine, Batch

    @app.route('/batch/<batch_id>')
    def show_batch(batch_id):
        batch = db.get_or_404(Batch, batch_id)
        return batch.id

    @app.post('/batch')
    @validate()
    def add_batch(form: schema.CreateBatchModel):
        batch = Batch(
            ref = form.id,
            sku = form.sku,
            qty= form.allocation
        )
        db.session.add(batch)
        db.session.commit()
        return schema.AllocateOrderResponseModel(batch_id=batch.id), 201
    

    @app.post('/allocate')
    @validate()
    def allocate_endpoint(form: schema.AllocateOrderLineModel):
        line = OrderLine(form.order_id, form.sku, form.qty)
        try:
            batch_id = services.allocate(line, db.session, BatchRepository(db.session))
        except (OutOfStock, services.InvalidSku) as e:
            return str(e), 400
        return batch_id, 201

    return app

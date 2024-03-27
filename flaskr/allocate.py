from flask import Blueprint, app
from flask_pydantic import validate
from flaskr.model import OrderLine, OutOfStock, CannotFindAllocation
from flaskr.schema import AllocateOrderLineModel, DeallocateOrderLineModel
from flaskr.repository import BatchRepository, ProductRepository
from flaskr.db import db

allocate = Blueprint("allocate", __name__, url_prefix="/allocate")
deallocate = Blueprint("deallocate", __name__, url_prefix="/deallocate")


@allocate.post("")
@validate()
def allocate_endpoint(form: AllocateOrderLineModel) -> tuple[str, int]:
    line = OrderLine(form.order_id, form.sku, form.qty)
    product = ProductRepository(db.session).get_by_sku(line.sku)
    try:
        batch_id = product.allocate(line)
        db.session.commit()
    except OutOfStock as e:
        return str(e), 400
    return batch_id, 201


@deallocate.post("")
@validate()
def deallocate_endpoint(form: DeallocateOrderLineModel) -> tuple[str, int]:
    line = OrderLine(form.order_id, form.sku, form.qty)
    product = ProductRepository(db.session).get_by_sku(line.sku)
    try:
        batch_id = product.deallocate(line.id)
        db.session.commit()
    except CannotFindAllocation as e:
        return str(e), 400
    return batch_id, 200

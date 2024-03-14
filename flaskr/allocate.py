from flask import Blueprint, app
from flask_pydantic import validate
from flaskr.model import OrderLine, OutOfStock
from flaskr.schema import AllocateOrderLineModel
import flaskr.services as services
from flaskr.repository import BatchRepository
from flaskr.db import db

bp = Blueprint('allocate', __name__, url_prefix='/allocate')

@bp.post('')
@validate()
def allocate_endpoint(form: AllocateOrderLineModel):
    line = OrderLine(form.order_id, form.sku, form.qty)
    try:
        batch_id = services.allocate(line, db.session, BatchRepository(db.session))
    except (OutOfStock, services.InvalidSku) as e:
        return str(e), 400
    return batch_id, 201
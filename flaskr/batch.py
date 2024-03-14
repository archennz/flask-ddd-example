from flask import Blueprint, app
from flask_pydantic import validate
from flaskr.db import db
from flaskr.model import Batch
from flaskr.schema import CreateBatchModel, AllocateOrderResponseModel

bp = Blueprint('batch', __name__, url_prefix='/batch')

@bp.route('/<batch_id>')
def show_batch(batch_id):
    batch = db.get_or_404(Batch, batch_id)
    return batch.id

@bp.post('')
@validate()
def add_batch(form: CreateBatchModel):
    batch = Batch(
        ref = form.id,
        sku = form.sku,
        qty= form.allocation
    )
    db.session.add(batch)
    db.session.commit()
    return AllocateOrderResponseModel(batch_id=batch.id), 201
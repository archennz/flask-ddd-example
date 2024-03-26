import flaskr.model as model
from flaskr.repository import BatchRepository
from sqlalchemy.orm import scoped_session
from flask_sqlalchemy.session import Session


def allocate(
    line: model.OrderLine, session: scoped_session[Session], repository: BatchRepository
) -> str:
    batches = repository.get_by_sku(line.sku)
    batch_id = model.allocate(line, batches)
    session.commit()
    return batch_id


def deallocate(
    line: model.OrderLine, session: scoped_session[Session], repository: BatchRepository
) -> str:
    batches = repository.get_by_sku(line.sku)
    batch_id = model.deallocate(line.id, batches)
    session.commit()
    return batch_id

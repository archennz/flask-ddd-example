import flaskr.model as model
from flaskr.repository import BatchRepository
from sqlalchemy.orm import scoped_session
from flask_sqlalchemy.session import Session


class InvalidSku(Exception): ...


def allocate(line: model.OrderLine, session: scoped_session[Session], repository: BatchRepository) -> str:
    batches = repository.get_by_sku(line.sku)
    if len(batches) == 0:
        raise InvalidSku(f"Invalid sku {line.sku}")
    batch_id = model.allocate(line, batches)
    session.commit()
    return batch_id

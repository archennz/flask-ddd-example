from sqlalchemy import select
from flaskr.model import Batch


class BatchRepository:
    def __init__(self, session) -> None:
        self.session = session

    def get_by_id(self, batch_id):
        stmt = select(Batch).where(Batch.id == batch_id)
        return self.session.scalars(stmt).first()

    def get_by_sku(self, sku):
        stmt = select(Batch).where(Batch.sku == sku)
        return self.session.scalars(stmt).all()

from typing import Iterator
from sqlalchemy import select
from flaskr.model import Batch, Product
from sqlalchemy.orm import scoped_session
from flask_sqlalchemy.session import Session
from collections.abc import Sequence


class BatchRepository:
    def __init__(self, session: scoped_session[Session]) -> None:
        self.session = session

    def get_by_id(self, batch_id: str) -> Batch | None:
        stmt = select(Batch).where(Batch.id == batch_id)
        return self.session.scalars(stmt).first()

    def get_by_sku(self, sku) -> Sequence[Batch]:
        stmt = select(Batch).where(Batch.sku == sku)
        return self.session.scalars(stmt).all()

class ProductRepository:
    def __init__(self, session: scoped_session[Session]) -> None:
        self.session = session

    def get_by_sku(self, sku) -> Product:
        stmt = select(Batch).where(Batch.sku == sku)
        batches = self.session.scalars(stmt).all()
        return Product(batches=batches, sku=sku)
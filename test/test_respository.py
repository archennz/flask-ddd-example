from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from flaskr.repository import BatchRepository, ProductRepository
from flaskr.model import Base, Batch, Product


@pytest.fixture()
def session():
    """Create in-memory sqlite db for testing"""
    # create in memory sqlite
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield Session(engine)


@pytest.fixture()
def populate_db(session):
    """Seed db with test objects"""

    def _populate_db(objects):
        session.add_all(objects)
        session.commit()

    return _populate_db


def generate_product(sku="sku") -> Product:
    """Build product with 1 batch

    Args:
        sku (str, optional): Defaults to "sku".

    Returns:
        Product:
    """
    return Product(batches=[Batch("batch-1", sku, 10)], sku=sku)


class TestBatchRepository:
    def test_get_by_id(self, session, populate_db):
        # arrange
        batch_in_repo = Batch("ref-1", "sku", 5, date(2011, 1, 1))
        populate_db([batch_in_repo])
        repository = BatchRepository(session)

        # act
        batch_retrieved = repository.get_by_id("ref-1")

        # assert
        assert batch_in_repo.id == batch_retrieved.id

    def test_get_by_id_not_there(self, ession):
        repository = BatchRepository(session)
        retrieved = repository.get_by_id("not-there")
        assert retrieved is None

    def test_get_by_sku(self, session, populate_db):
        # arrange
        batch_in_repo = Batch("ref-1", "sku", 5, date(2011, 1, 1))
        populate_db([batch_in_repo])
        repository = BatchRepository(session)

        # act
        batch_retrieved = repository.get_by_sku("sku")

        # assert
        assert len(batch_retrieved) == 1
        assert batch_retrieved[0].id == batch_in_repo.id

    def test_get_by_sku_not_there(self, session):
        repository = BatchRepository(session)
        retrieved = repository.get_by_sku("not-there")
        assert len(retrieved) == 0


class TestProductRepository:
    def test_product_get_by_sku(self, session, populate_db):
        product = generate_product()
        populate_db(product.batches)

        repository = ProductRepository(session)
        product_retrieved = repository.get_by_sku(product.sku)
        assert product.sku == product_retrieved.sku
        assert product.batches == product_retrieved.batches

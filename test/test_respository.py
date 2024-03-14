from datetime import date
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from repository import BatchRepository
from model import Base, Batch


@pytest.fixture()
def session():
    # create in memory sqlite
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield Session(engine)


@pytest.fixture()
def populate_db(session):
    def _populate_db(objects):
        session.add_all(objects)
        session.commit()
    return _populate_db


def test_get_by_id(session,populate_db):
    # arrange
    batch_in_repo = Batch("ref-1", "sku", 5, date(2011, 1, 1))
    populate_db([batch_in_repo])
    repository = BatchRepository(session)

    # act
    batch_retrieved = repository.get_by_id("ref-1")

    # assert 
    assert batch_in_repo.id == batch_retrieved.id


def test_get_by_id_not_there(session):
    repository = BatchRepository(session)
    retrieved = repository.get_by_id("not-there")
    assert retrieved is None


def test_get_by_sku(session,populate_db):
    # arrange
    batch_in_repo = Batch("ref-1", "sku", 5, date(2011, 1, 1))
    populate_db([batch_in_repo])
    repository = BatchRepository(session)

    # act
    batch_retrieved = repository.get_by_sku("sku")

    # assert 
    assert len(batch_retrieved) == 1
    assert batch_retrieved[0].id == batch_in_repo.id


def test_get_by_sku_not_there(session):
    repository = BatchRepository(session)
    retrieved = repository.get_by_sku("not-there")
    assert len(retrieved) == 0 


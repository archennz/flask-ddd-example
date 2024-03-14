from typing import List
import pytest
import flaskr.model as model
import flaskr.services as services

class FakeBatchRepository():
    def __init__(self, batches: List[model.Batch]) -> None:
        self._batches = set(batches)

    def get_by_id(self, batch_id: str):
        return next(b for b in self._batches if b.id == batch_id)

    def get_by_sku(self, sku: str):
        return [x for x in self._batches if x.sku == sku]

class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_returns_allocation():
    line = model.OrderLine("o1", "COMPLICATED-LAMP", 10)
    batch = model.Batch("b1", "COMPLICATED-LAMP", 100, eta=None)
    repo = FakeBatchRepository([batch])

    result = services.allocate(line, FakeSession(), repo)
    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "AREALSKU", 100, eta=None)
    repo = FakeBatchRepository([batch])

    with pytest.raises(services.InvalidSku, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, FakeSession(), repo)


def test_commits():
    line = model.OrderLine("o1", "OMINOUS-MIRROR", 10)
    batch = model.Batch("b1", "OMINOUS-MIRROR", 100, eta=None)
    repo = FakeBatchRepository([batch])
    session = FakeSession()

    services.allocate(line, session, repo)
    assert session.committed is True

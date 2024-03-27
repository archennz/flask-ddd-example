from typing import Tuple
import pytest
import uuid
from flaskr.model import Batch, OrderLine
from datetime import date
from flaskr.db import db
from flaskr.schema import (
    CreateBatchModel,
    AllocateOrderLineModel,
    DeallocateOrderLineModel,
)

from flask import Flask
from flask.testing import FlaskClient


def random_suffix() -> str:
    return uuid.uuid4().hex[:6]


def random_sku(name: str ="") -> str:
    return f"sku-{name}-{random_suffix()}"


def random_batchid(name: str="") -> str:
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name: str="") -> str:
    return f"order-{name}-{random_suffix()}"


@pytest.fixture()
def set_up_batches(add_test_data):
    """Helper function to add three batches into db"""
    sku, othersku = random_sku(), random_sku("other")
    earlybatch, laterbatch, otherbatch = (
        random_batchid(1),
        random_batchid(2),
        random_batchid(3),
    )

    add_test_data(
        [
            Batch(earlybatch, sku, 100, date(2011, 1, 1)),
            Batch(laterbatch, sku, 100, date(2011, 1, 2)),
            Batch(otherbatch, othersku, 100, None),
        ]
    )

    return sku, othersku, earlybatch, laterbatch, otherbatch


@pytest.fixture()
def set_up_batches_with_allocation(add_test_data) -> Tuple[str, str, int, str]:
    """Helper function to add three batches into db with one allocation already done"""
    sku = random_sku()
    batch_id = random_batchid()
    order_id = "id"
    qty = 5
    orderline = OrderLine("id", sku, 5)
    batch = Batch(batch_id, sku, 40)
    batch.allocate(orderline)
    add_test_data([batch])

    return (order_id, sku, qty, batch_id)


class TestBatchResource:
    def test_can_add_batch(self, client: FlaskClient, app: Flask):
        batch_id = "1"
        data = CreateBatchModel(id=batch_id, sku="sku", allocation=3)
        res = client.post("/batch", data=data.model_dump())

        assert res.status_code == 201

        with app.app_context():
            batch = db.session.get(Batch, batch_id)
            assert batch is not None

    def test_api_returns_batch(self, client: FlaskClient, add_test_data):
        batch_id = random_batchid()
        batch = Batch(batch_id, "sku", 5)

        add_test_data([batch])

        res = client.get(f"/batch/{batch_id}")
        assert res.text == batch_id
        assert res.status_code == 200


class TestAllocateResource:
    def test_api_returns_allocation(self, client: FlaskClient, set_up_batches, app: Flask):
        sku, _, earlybatch, _, _ = set_up_batches
        order_id = random_orderid()
        data = AllocateOrderLineModel(order_id=order_id, sku=sku, qty=3)
        res = client.post("/allocate", data=data.model_dump())

        assert res.status_code == 201
        assert res.text == earlybatch

        with app.app_context():
            batch_altered = db.session.get(Batch, earlybatch)
            assert batch_altered is not None
            assert order_id in list(batch_altered.allocation_ids)


    def test_api_returns_400_if_cannot_allocate(self, client: FlaskClient, set_up_batches):
        data = AllocateOrderLineModel(order_id=random_orderid(), sku="sku", qty=3)
        res = client.post("/allocate", data=data.model_dump())

        assert res.status_code == 400
        assert "Out of stock" in res.text



class TestDeallocateResource:
    def test_api_can_deallocate(self, client: FlaskClient, set_up_batches_with_allocation, app: Flask):
        id, sku, qty, batch_id = set_up_batches_with_allocation
        data = DeallocateOrderLineModel(order_id=id, sku=sku, qty=qty)

        res = client.post("/deallocate", data=data.model_dump())
        assert res.status_code == 200
        assert res.text == batch_id

        with app.app_context():
            batch = db.session.get(Batch, batch_id)
            assert batch is not None
            assert len(batch.allocation_ids) == 0

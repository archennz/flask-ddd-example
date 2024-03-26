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


def random_suffix():
    return uuid.uuid4().hex[:6]


def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"


def random_batchid(name=""):
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name=""):
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
    def test_can_add_batch(self, client, app):
        data = CreateBatchModel(id="1", sku="sku", allocation=3)
        res = client.post("/batch", data=data.model_dump())

        assert res.status_code == 201

    def test_api_returns_batch(self, client, add_test_data):
        batch_id = random_batchid()
        batch = Batch(batch_id, "sku", 5)

        add_test_data([batch])

        res = client.get(f"/batch/{batch_id}")
        assert res.text == batch_id


class TestAllocateResource:
    def test_api_returns_allocation(self, client, set_up_batches):
        sku, _, earlybatch, _, _ = set_up_batches
        data = AllocateOrderLineModel(order_id=random_orderid(), sku=sku, qty=3)
        res = client.post("/allocate", data=data.model_dump())

        assert res.status_code == 201
        assert res.text == earlybatch


    def test_api_returns_400_if_cannot_allocate(self, client, set_up_batches):
        data = AllocateOrderLineModel(order_id=random_orderid(), sku="sku", qty=3)
        res = client.post("/allocate", data=data.model_dump())

        assert res.status_code == 400
        assert "Out of stock" in res.text



class TestDeallocateResource:
    def test_api_can_deallocate(self, client, set_up_batches_with_allocation):
        id, sku, qty, batch_id = set_up_batches_with_allocation
        data = DeallocateOrderLineModel(order_id=id, sku=sku, qty=qty)

        res = client.post("/deallocate", data=data.model_dump())
        assert res.text == batch_id

import pytest
import uuid
from model import Batch
from datetime import date
from flaskr.db import db

def random_suffix():
    return uuid.uuid4().hex[:6]

def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"

def random_batchid(name=""):
    return f"batch-{name}-{random_suffix()}"

def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


def test_api_returns_allocation(app, client):
    sku, othersku = random_sku(), random_sku("other")
    earlybatch, laterbatch, otherbatch= random_batchid(1), random_batchid(2), random_batchid(3)

    with app.app_context():
        db.session.add_all(
            [
                Batch(earlybatch, sku, 100, date(2011, 1, 1)),
                Batch(laterbatch, sku, 100, date(2011, 1, 2)),
                Batch(otherbatch, othersku, 100, None)
            ]
        )
        db.session.commit()
    
    data = {"order_id": random_orderid(), "sku": sku, "qty": 3}
    res = client.post("/allocate", data = data)

    assert res.status_code == 201
    assert res.text == earlybatch


def test_api_returns_batch(app, client):
    batch_id = random_batchid()
    batch = Batch(batch_id, "sku", 5)

    with app.app_context():
        db.session.add(batch)
        db.session.commit()
    
    res = client.get(f"/batch/{batch_id}")
    assert res.text == batch_id


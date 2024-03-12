import pytest
import uuid
from model import Batch
from datetime import date
from flaskr.db import db

def test_api_returns_test_2(client):
    response = client.get("/test-2")

def random_suffix():
    return uuid.uuid4().hex[.6]

def random_sku(name=""):
    return f"sku-{name}-{random_suffix()}"

def random_batchid(name=""):
    return f"batch-{name}-{random_suffix()}"

def random_orderid(name=""):
    return f"order-{name}-{random_suffix()}"


# def test_api_returns_allocation(app):
#     sku, othersku = random_sku(), random_sku("other")
#     earlybatch = random_batchid(1)
#     laterbatch = random_batchid(2)
#     otherbatch = random_batchid(3)

#     batch = Batch(earlybatch, sku, 10, date(2012, 10, 23))

#     with app.app_context():
#         db.session.add(batch)

#     with app.test_request_context(

#     )

#     data = {"orderid": random_orderid, "sku": sku, "qty": 3}
#     response = client.post("/allocate", json=data)

#     assert response.status_code == 201
#     assert response.json()["batchid"] == earlybatch


# def test_api_returns_batch_again(app, client):
#     batch = Batch(random_batchid(), random_sku(), 5)
    
#     with app.app_context():
#         db.session.add(batch)
#         db.session.commit()
    
#     res = client.get(f"/batch/{batch.id}")
#     assert res.code == 200

# random fake test
# this is using the real database, would be good if it used a test one?
def test_api_returns_batch(app, client):
    with app.app_context():
        batch = Batch("1", "sku", 5)
        db.session.add(batch)
        db.session.commit()
    
    res = client.get("/batch/1")
    assert res.text == "1"
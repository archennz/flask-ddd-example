from datetime import date, timedelta
import pytest
from flaskr.model import allocate, OrderLine, Batch, OutOfStock, deallocate, CannotDeallocate

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)
    line = OrderLine("oref", "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch("speedy-batch", "MINIMALIST-SPOON", 100, eta=today)
    medium = Batch("normal-batch", "MINIMALIST-SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "MINIMALIST-SPOON", 100, eta=later)
    line = OrderLine("order1", "MINIMALIST-SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch("in-stock-batch-ref", "HIGHBROW-POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "HIGHBROW-POSTER", 100, eta=tomorrow)
    line = OrderLine("oref", "HIGHBROW-POSTER", 10)
    allocation = allocate(line, [in_stock_batch, shipment_batch])
    assert allocation == in_stock_batch.id


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch("batch1", "SMALL-FORK", 10, eta=today)
    allocate(OrderLine("order1", "SMALL-FORK", 10), [batch])

    with pytest.raises(OutOfStock, match="SMALL-FORK"):
        allocate(OrderLine("order2", "SMALL-FORK", 1), [batch])


def test_raises_out_of_stock_exception_if_no_batch_avilable():
    with pytest.raises(OutOfStock, match="Out of stock"):
        allocate(OrderLine("order-1", "sku", 1), [])


def test_returns_batch_id_if_can_deallocate():
    sku = "MINIMALIST-SPOON"
    batch = Batch("speedy-batch", sku , 100)
    line = OrderLine("order-id", sku, 4)
    batch.allocate(line)

    batch_id = deallocate(line, [batch])
    assert batch_id == batch.id


def test_returns_null_if_cannot_deallocate():
    batch = Batch("speedy-batch", "MINIMALIST-SPOON" , 100)
    line = OrderLine("order-id", "different-sku", 30)
    with pytest.raises(CannotDeallocate, match="have not been allocated"):
        deallocate(line, [batch])
from datetime import date, timedelta
import pytest
from flaskr.model import OrderLine, Batch, OutOfStock, deallocate, Product, CannotFindAllocation

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def make_product_and_orderline(sku: str, etas: list[date | None], line_qty: int, batch_qty: int = 100) -> tuple[Product, OrderLine]:
    batches_list = []
    for index, eta in enumerate(etas):
        batches_list.append(
            Batch(f"batch-{index}", sku, batch_qty, eta=eta)
        )
    product =  Product(
        batches= batches_list,
        sku =sku
    )
    line = OrderLine(orderid="order-123", sku=sku, qty=line_qty)

    return (product, line)


def test_prefers_current_stock_batches_to_shipments():
    product, line = make_product_and_orderline("sku-1", [None, tomorrow], 10)

    batchid = product.allocate(line)
    assert batchid == "batch-0"
    assert product.batches[0].available_quantity == 90
    assert product.batches[1].available_quantity == 100


def test_prefers_earlier_batches():
    product, line = make_product_and_orderline("sku-1", [today, tomorrow, later], 10)

    batchid = product.allocate(line)
    assert batchid == "batch-0"
    assert product.batches[0].available_quantity == 90
    assert product.batches[1].available_quantity == 100
    assert product.batches[2].available_quantity == 100


def test_raises_out_of_stock_exception_if_cannot_allocate():
    product, line = make_product_and_orderline("sku-1", [today], line_qty=10, batch_qty=1)

    with pytest.raises(OutOfStock):
        product.allocate(line)


def test_raises_out_of_stock_exception_if_no_batch_available():
    product, line = make_product_and_orderline("sku-1", [], line_qty=10, batch_qty=1)
    with pytest.raises(OutOfStock, match="Out of stock"):
        product.allocate(OrderLine("order-1", "sku", 1))


def test_returns_batch_id_if_can_deallocate():
    sku = "sku-1"
    product, line = make_product_and_orderline(sku, [None], 4)
    another_line_qty = 10
    another_line = OrderLine("another-order", sku, another_line_qty)
    product.allocate(line)
    product.allocate(another_line)
    batch_id = product.deallocate(line.id)
    assert batch_id == product.batches[0].id
    assert product.batches[0].available_quantity == 100 - another_line_qty


def test_returns_null_if_cannot_deallocate():
    product, _ = make_product_and_orderline("sku-1", [None], 4)
    line = OrderLine("order-id", "different-sku", 30)
    with pytest.raises(CannotFindAllocation, match="have not been allocated"):
        product.deallocate(line.id)
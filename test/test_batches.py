from datetime import date
from flaskr.model import Batch, OrderLine, Product


def make_batch_and_line(
    sku: str, batch_qty: int, line_qty: int
) -> tuple[Batch, OrderLine]:
    """Build batch and orderline for testing

    Args:
        sku (str): shared sku for batch and orderline
        batch_qty (int): Batch quantity
        line_qty (int): Orderline quantity

    Returns:
        tuple[Batch, OrderLine]:
    """
    return (
        Batch("batch-001", sku, batch_qty, eta=date.today()),
        OrderLine(orderid="order-123", sku=sku, qty=line_qty),
    )


class TestBatchAllocate:
    def test_allocating_to_a_batch_reduces_the_available_quantity(self):
        batch = Batch("batch-001", "SMALL-TABLE", qty=20, eta=date.today())
        line = OrderLine("order-ref", "SMALL-TABLE", 2)

        batch.allocate(line)

        assert batch.available_quantity == 18

    def test_can_allocate_if_available_greater_than_required(self):
        large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)
        assert large_batch.can_allocate(small_line)

    def test_cannot_allocate_if_available_smaller_than_required(self):
        small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)
        assert small_batch.can_allocate(large_line) is False

    def test_can_allocate_if_available_equal_to_required(self):
        batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)
        assert batch.can_allocate(line)

    def test_cannot_allocate_if_skus_do_not_match(self):
        batch = Batch("batch-001", "UNCOMFORTABLE-CHAIR", 100, eta=None)
        different_sku_line = OrderLine("order-123", "EXPENSIVE-TOASTER", 10)
        assert batch.can_allocate(different_sku_line) is False

    def test_allocation_is_idempotent(self):
        batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
        batch.allocate(line)
        batch.allocate(line)
        assert batch.available_quantity == 18


class TestBatchDeallocate:
    def test_deallocate(self):
        batch, line = make_batch_and_line("EXPENSIVE-FOOTSTOOL", 20, 2)
        batch.allocate(line)
        batch.can_deallocate == True
        batch_id = batch.deallocate(line.id)
        assert batch.available_quantity == 20

    def test_can_only_deallocate_allocated_lines(self):
        batch, unallocated_line = make_batch_and_line("DECORATIVE-TRINKET", 20, 2)
        batch.deallocate(unallocated_line)
        assert batch.can_deallocate(unallocated_line) == False
        assert batch.available_quantity == 20

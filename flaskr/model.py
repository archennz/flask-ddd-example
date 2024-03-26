from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Any, Optional, List, Set

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, Date, ForeignKey, Integer, String, Table
from collections.abc import Sequence


class OutOfStock(Exception): ...


class CannotFindAllocation(Exception): ...


def allocate(line: OrderLine, batches: Sequence[Batch]) -> str:
    try:
        batch = next(b for b in sorted(batches) if b.can_allocate(line))
        batch.allocate(line)
        return batch.id
    except StopIteration:
        raise OutOfStock(f"Out of stock for sku {line.sku}")


def deallocate(line_id: str, batches: Sequence[Batch]) -> str:
    for batch in batches:
        if batch.can_deallocate(line_id):
            batch.deallocate(line_id)
            return batch.id
    raise CannotFindAllocation(f"order {line_id} have not been allocated")


class Base(DeclarativeBase):
    pass


class OrderLine(Base):
    __tablename__ = "orderline"
    id: Mapped[str] = mapped_column(primary_key=True)
    sku: Mapped[str]
    qty: Mapped[int]

    def __init__(self, orderid: str, sku: str, qty: int):
        self.id = orderid
        self.sku = sku
        self.qty = qty


allocations = Table(
    "allocation",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("orderline_id", ForeignKey("orderline.id")),
    Column("batch_id", ForeignKey("batch.id")),
)


class Batch(Base):
    __tablename__ = "batch"
    id: Mapped[str] = mapped_column(primary_key=True)
    sku: Mapped[str]
    eta: Mapped[date] = mapped_column(nullable=True)
    _purchased_quantity: Mapped[int]
    _allocations: Mapped[Set["OrderLine"]] = relationship(secondary=allocations)

    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date] = None):
        self.id = ref
        self.sku = sku
        self.eta = eta  # type: ignore #sqlalchemy orm magic
        self._purchased_quantity = qty
        self._allocations = set()  # type: Set[OrderLine]

    def __repr__(self) -> str:
        return f"<Batch {self.id}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Batch):
            return False
        return other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __gt__(self, other: Batch) -> bool:
        if self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocations.add(line)

    def deallocate(self, line_id: str) -> None:
        if self.can_deallocate(line_id):
            self._allocations = set(
                filter(lambda allocation: allocation.id != line_id, self._allocations)
            )

    @property
    def allocated_quantity(self) -> int:
        return sum(line.qty for line in self._allocations)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    @property
    def allocation_ids(self) -> Sequence[str]:
        return [allocation.id for allocation in self._allocations]

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty

    def can_deallocate(self, line_id: str) -> bool:
        return line_id in self.allocation_ids


class Product:
    batches: Sequence[Batch]
    sku: str

    def __init__(self, batches: Sequence[Batch], sku: str) -> None:
        self.batches = batches
        self.sku = sku

    def allocate(self, line: OrderLine) -> str:
        try:
            batch = next(b for b in sorted(self.batches) if b.can_allocate(line))
            batch.allocate(line)
            return batch.id
        except StopIteration:
            raise OutOfStock(f"Out of stock for sku {line.sku}")

    def deallocate(self, line_id: str) -> str:
        for batch in self.batches:
            if batch.can_deallocate(line_id):
                batch.deallocate(line_id)
                return batch.id
        raise CannotFindAllocation(f"order {line_id} have not been allocated")

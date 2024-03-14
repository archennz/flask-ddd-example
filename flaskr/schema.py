from typing import Optional
from pydantic import BaseModel
from datetime import date

class CreateBatchModel(BaseModel):
    id: str
    sku: str
    allocation: int
    eta: Optional[date] = None


class AllocateOrderLineModel(BaseModel):
    order_id: str
    sku: str
    qty: int

class AllocateOrderResponseModel(BaseModel):
    batch_id: str
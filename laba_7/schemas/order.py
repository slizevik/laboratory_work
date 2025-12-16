# schemas/order.py
from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class OrderCreate(BaseModel):
    user_id: str
    product_ids: List[str]  # ID продуктов, которые добавляются в заказ

class OrderUpdate(BaseModel):
    status: Optional[str] = None

class OrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    user_id: str
    status: str
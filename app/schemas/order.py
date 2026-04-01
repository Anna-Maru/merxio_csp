from datetime import datetime
from pydantic import BaseModel
from app.models.order import OrderStatus


class OrderItemOut(BaseModel):
    id: int
    product_id: int | None
    product_name: str
    price_at_order: int
    quantity: int

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_price: int
    created_at: datetime
    items: list[OrderItemOut]

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

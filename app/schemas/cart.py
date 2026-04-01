from pydantic import BaseModel
from app.schemas.product import ProductOut


class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemOut(BaseModel):
    id: int
    product_id: int
    quantity: int
    product: ProductOut

    model_config = {"from_attributes": True}


class CartOut(BaseModel):
    id: int
    user_id: int
    items: list[CartItemOut]
    total: int = 0

    model_config = {"from_attributes": True}

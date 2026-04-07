from datetime import datetime
from pydantic import BaseModel, field_validator


class ProductCreate(BaseModel):
    name: str
    description: str | None = None
    price: int
    category: str | None = None

    @field_validator("price")
    @classmethod
    def check_price(cls, v):
        if v <= 0:
            raise ValueError("Цена должна быть больше нуля")
        return v


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    price: int | None = None
    category: str | None = None
    is_active: bool | None = None


class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: int
    category: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

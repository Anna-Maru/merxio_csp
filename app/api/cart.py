from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.base import get_db
from app.models.user import User
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartOut
from app.services.cart_service import (
    get_or_create_cart,
    add_items,
    update_item,
    remove_item,
    clear_cart,
    calc_total,
)

router = APIRouter(prefix="/cart", tags=["cart"])


def _build_response(cart, total: int) -> dict:
    return {
        "id": cart.id,
        "user_id": cart.user_id,
        "items": cart.items,
        "total": total,
    }


@router.get("/", response_model=CartOut)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = await get_or_create_cart(current_user.id, db)
    return _build_response(cart, calc_total(cart))


@router.post("/items", response_model=CartOut)
async def add_to_cart(
    items: list[CartItemAdd],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = await add_items(
            current_user.id,
            [i.model_dump() for i in items],
            db,
        )
        return _build_response(cart, calc_total(cart))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/items/{item_id}", response_model=CartOut)
async def change_quantity(
    item_id: int,
    data: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = await update_item(current_user.id, item_id, data.quantity, db)
        return _build_response(cart, calc_total(cart))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/items/{item_id}", response_model=CartOut)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart = await remove_item(current_user.id, item_id, db)
        return _build_response(cart, calc_total(cart))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/", response_model=CartOut)
async def clean_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = await clear_cart(current_user.id, db)
    return _build_response(cart, calc_total(cart))


@router.get("/total")
async def get_total(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    cart = await get_or_create_cart(current_user.id, db)
    return {"total": calc_total(cart)}

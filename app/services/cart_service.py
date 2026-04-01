from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.models.product import Product


async def get_or_create_cart(user_id: int, db: AsyncSession) -> Cart:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    cart = result.scalar_one_or_none()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        await db.commit()
        await db.refresh(cart)
        result = await db.execute(
            select(Cart)
            .where(Cart.id == cart.id)
            .options(selectinload(Cart.items).selectinload(CartItem.product))
        )
        cart = result.scalar_one()
    return cart


async def add_items(
    user_id: int,
    items_data: list[dict],
    db: AsyncSession,
) -> Cart:
    cart = await get_or_create_cart(user_id, db)

    for item_data in items_data:
        product_id = item_data["product_id"]
        quantity = item_data.get("quantity", 1)

        product_result = await db.execute(
            select(Product).where(Product.id == product_id, Product.is_active == True)
        )
        product = product_result.scalar_one_or_none()
        if not product:
            raise ValueError(f"Товар {product_id} не найден или неактивен")

        existing_result = await db.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id,
            )
        )
        existing = existing_result.scalar_one_or_none()

        if existing:
            existing.quantity += quantity
        else:
            db.add(CartItem(cart_id=cart.id, product_id=product_id, quantity=quantity))

    await db.commit()
    return await get_or_create_cart(user_id, db)


async def update_item(
    user_id: int,
    item_id: int,
    quantity: int,
    db: AsyncSession,
) -> Cart:
    cart = await get_or_create_cart(user_id, db)

    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise ValueError("Позиция не найдена в корзине")

    if quantity <= 0:
        await db.delete(item)
    else:
        item.quantity = quantity

    await db.commit()
    return await get_or_create_cart(user_id, db)


async def remove_item(user_id: int, item_id: int, db: AsyncSession) -> Cart:
    cart = await get_or_create_cart(user_id, db)

    result = await db.execute(
        select(CartItem).where(CartItem.id == item_id, CartItem.cart_id == cart.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise ValueError("Позиция не найдена в корзине")

    await db.delete(item)
    await db.commit()
    return await get_or_create_cart(user_id, db)


async def clear_cart(user_id: int, db: AsyncSession) -> Cart:
    cart = await get_or_create_cart(user_id, db)
    for item in cart.items:
        await db.delete(item)
    await db.commit()
    return await get_or_create_cart(user_id, db)


def calc_total(cart: Cart) -> int:
    return sum(item.product.price * item.quantity for item in cart.items)

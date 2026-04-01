from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, OrderStatus
from app.schemas.order import OrderStatusUpdate


async def create_order(user_id: int, db: AsyncSession) -> Order:
    result = await db.execute(
        select(Cart)
        .where(Cart.user_id == user_id)
        .options(selectinload(Cart.items).selectinload(CartItem.product))
    )
    cart = result.scalar_one_or_none()

    if not cart or not cart.items:
        raise ValueError("Корзина пуста")

    total = sum(item.product.price * item.quantity for item in cart.items)

    order = Order(user_id=user_id, total_price=total)
    db.add(order)
    await db.flush()

    for item in cart.items:
        db.add(
            OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name,
                price_at_order=item.product.price,
                quantity=item.quantity,
            )
        )
        await db.delete(item)

    await db.commit()
    await db.refresh(order)
    return await get_order_by_id(order.id, db)


async def get_order_by_id(order_id: int, db: AsyncSession) -> Order:
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("Заказ не найден")
    return order


async def get_user_orders(user_id: int, db: AsyncSession) -> list[Order]:
    result = await db.execute(
        select(Order)
        .where(Order.user_id == user_id)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
    )
    return result.scalars().all()


async def update_order_status(
    order_id: int, data: OrderStatusUpdate, db: AsyncSession
) -> Order:
    order = await get_order_by_id(order_id, db)
    order.status = data.status
    await db.commit()
    await db.refresh(order)
    return order

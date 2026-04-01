from datetime import datetime, timedelta
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User


async def get_summary(
    db: AsyncSession,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    query = select(Order).where(Order.status != OrderStatus.cancelled)
    if date_from:
        query = query.where(Order.created_at >= date_from)
    if date_to:
        query = query.where(Order.created_at <= date_to)

    result = await db.execute(query)
    orders = result.scalars().all()

    total_revenue = sum(o.total_price for o in orders)
    total_orders = len(orders)
    avg_check = total_revenue // total_orders if total_orders else 0

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "avg_check": avg_check,
        "date_from": date_from,
        "date_to": date_to,
    }


async def get_top_products(db: AsyncSession, limit: int = 10) -> list[dict]:
    result = await db.execute(
        select(
            OrderItem.product_name,
            OrderItem.product_id,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(
                OrderItem.price_at_order * OrderItem.quantity
            ).label("total_revenue"),
        )
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status != OrderStatus.cancelled)
        .group_by(OrderItem.product_id, OrderItem.product_name)
        .order_by(func.sum(OrderItem.price_at_order * OrderItem.quantity).desc())
        .limit(limit)
    )
    rows = result.all()
    return [
        {
            "product_id": r.product_id,
            "product_name": r.product_name,
            "total_qty": r.total_qty,
            "total_revenue": r.total_revenue,
        }
        for r in rows
    ]


async def get_sales_by_category(db: AsyncSession) -> list[dict]:
    result = await db.execute(
        select(
            Product.category,
            func.sum(OrderItem.quantity).label("total_qty"),
            func.sum(
                OrderItem.price_at_order * OrderItem.quantity
            ).label("total_revenue"),
        )
        .join(Product, Product.id == OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.status != OrderStatus.cancelled)
        .group_by(Product.category)
        .order_by(func.sum(OrderItem.price_at_order * OrderItem.quantity).desc())
    )
    rows = result.all()
    return [
        {
            "category": r.category or "Без категории",
            "total_qty": r.total_qty,
            "total_revenue": r.total_revenue,
        }
        for r in rows
    ]


async def get_sales_dynamics(
    db: AsyncSession,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    group_by: str = "day",
) -> list[dict]:
    if not date_from:
        date_from = datetime.utcnow() - timedelta(days=30)
    if not date_to:
        date_to = datetime.utcnow()

    if group_by == "week":
        trunc = func.date_trunc("week", Order.created_at)
    else:
        trunc = func.date_trunc("day", Order.created_at)

    result = await db.execute(
        select(
            trunc.label("period"),
            func.count(Order.id).label("orders_count"),
            func.sum(Order.total_price).label("revenue"),
        )
        .where(Order.status != OrderStatus.cancelled)
        .where(Order.created_at >= date_from)
        .where(Order.created_at <= date_to)
        .group_by("period")
        .order_by("period")
    )
    rows = result.all()
    return [
        {
            "period": str(r.period)[:10],
            "orders_count": r.orders_count,
            "revenue": r.revenue,
        }
        for r in rows
    ]


async def get_new_users(
    db: AsyncSession,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict:
    query = select(func.count(User.id))
    if date_from:
        query = query.where(User.created_at >= date_from)
    if date_to:
        query = query.where(User.created_at <= date_to)
    result = await db.execute(query)
    return {"new_users": result.scalar()}

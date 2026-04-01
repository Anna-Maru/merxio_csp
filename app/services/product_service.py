from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


async def get_products(
    db: AsyncSession,
    category: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    search: str | None = None,
    order_by: str = "name",
) -> list[Product]:
    query = select(Product).where(Product.is_active == True)

    if category:
        query = query.where(Product.category == category)
    if min_price is not None:
        query = query.where(Product.price >= min_price)
    if max_price is not None:
        query = query.where(Product.price <= max_price)
    if search:
        query = query.where(Product.name.ilike(f"%{search}%"))

    order_map = {
        "name": Product.name,
        "price_asc": Product.price,
        "price_desc": Product.price.desc(),
        "created_at": Product.created_at.desc(),
    }
    query = query.order_by(order_map.get(order_by, Product.name))

    result = await db.execute(query)
    return result.scalars().all()


async def get_product_by_id(product_id: int, db: AsyncSession) -> Product:
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise ValueError("Товар не найден")
    return product


async def create_product(data: ProductCreate, db: AsyncSession) -> Product:
    product = Product(**data.model_dump())
    db.add(product)
    await db.commit()
    await db.refresh(product)
    return product


async def update_product(
    product_id: int, data: ProductUpdate, db: AsyncSession
) -> Product:
    product = await get_product_by_id(product_id, db)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.commit()
    await db.refresh(product)
    return product


async def delete_product(product_id: int, db: AsyncSession) -> None:
    product = await get_product_by_id(product_id, db)
    await db.delete(product)
    await db.commit()
    
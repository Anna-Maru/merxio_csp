from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
)

async_session_maker = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


# Импорты нужны для Alembic — не удалять!
from app.models.user import User        # noqa: F401, E402
from app.models.product import Product  # noqa: F401, E402
from app.models.cart import Cart, CartItem  # noqa: F401, E402
from app.models.order import Order, OrderItem # noqa: F401, E402

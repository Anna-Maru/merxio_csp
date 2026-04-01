import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DATABASE_URL, echo=False)

async_session_test = sessionmaker(
    engine_test, class_=AsyncSession, expire_on_commit=False
)


async def override_get_db():
    async with async_session_test() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def registered_user(client):
    response = await client.post(
        "/auth/register",
        json={
            "full_name": "Test User",
            "email": "test@example.com",
            "phone": "+71234567890",
            "password": "TestPass!",
            "password_confirm": "TestPass!",
        },
    )
    return response.json()


@pytest_asyncio.fixture
async def auth_headers(client, registered_user):
    response = await client.post(
        "/auth/login",
        json={
            "login": "test@example.com",
            "password": "TestPass!",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_headers(client):
    await client.post(
        "/auth/register",
        json={
            "full_name": "Admin User",
            "email": "admin@example.com",
            "phone": "+79999999999",
            "password": "AdminPass!",
            "password_confirm": "AdminPass!",
        },
    )
    async with async_session_test() as session:
        from sqlalchemy import select
        from app.models.user import User

        result = await session.execute(
            select(User).where(User.email == "admin@example.com")
        )
        user = result.scalar_one()
        user.is_admin = True
        await session.commit()

    response = await client.post(
        "/auth/login",
        json={
            "login": "admin@example.com",
            "password": "AdminPass!",
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def product(client, admin_headers):
    response = await client.post(
        "/products/",
        json={
            "name": "Test Product",
            "description": "Test description",
            "price": 1000,
            "category": "Electronics",
        },
        headers=admin_headers,
    )
    return response.json()

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User
from app.schemas.user import UserRegister


async def register_user(data: UserRegister, db: AsyncSession) -> User:
    result = await db.execute(
        select(User).where(or_(User.email == data.email, User.phone == data.phone))
    )
    existing = result.scalar_one_or_none()
    if existing:
        if existing.email == data.email:
            raise ValueError("Пользователь с таким email уже существует")
        raise ValueError("Пользователь с таким телефоном уже существует")

    user = User(
        full_name=data.full_name,
        email=data.email,
        phone=data.phone,
        hashed_password=hash_password(data.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_user(login: str, password: str, db: AsyncSession) -> str:
    result = await db.execute(
        select(User).where(or_(User.email == login, User.phone == login))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.hashed_password):
        raise ValueError("Неверный логин или пароль")
    if not user.is_active:
        raise ValueError("Аккаунт заблокирован")

    return create_access_token({"sub": str(user.id), "is_admin": user.is_admin})

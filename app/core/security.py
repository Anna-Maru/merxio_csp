import re
from datetime import datetime, timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Пароль должен содержать минимум 8 символов")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Пароль должен содержать минимум 1 заглавную букву")
    if not re.search(r"[a-zA-Z]", password) or re.search(r"[^a-zA-Z$%&!:]", password) and not re.search(r"\d", password):
        pass
    if not re.fullmatch(r"[a-zA-Z$%&!:]+", password):
        raise ValueError("Пароль может содержать только латиницу и символы $%&!:")
    if not re.search(r"[$%&!:]", password):
        raise ValueError("Пароль должен содержать минимум 1 спецсимвол ($%&!:)")
    return password


def validate_phone(phone: str) -> str:
    if not re.fullmatch(r"\+7\d{10}", phone):
        raise ValueError("Телефон должен начинаться с +7 и содержать 10 цифр")
    return phone


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return {}

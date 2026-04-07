from pydantic import BaseModel, EmailStr, field_validator
from app.core.security import validate_password, validate_phone


class UserRegister(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    password: str
    password_confirm: str

    @field_validator("phone")
    @classmethod
    def check_phone(cls, v):
        return validate_phone(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v):
        return validate_password(v)

    @field_validator("password_confirm")
    @classmethod
    def check_passwords_match(cls, v, info):
        if info.data.get("password") and v != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return v


class UserLogin(BaseModel):
    login: str  # email или телефон
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    is_active: bool
    is_admin: bool

    model_config = {"from_attributes": True}


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

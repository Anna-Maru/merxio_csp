from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import get_db
from app.schemas.user import UserRegister, UserLogin, UserOut, TokenOut
from app.services.user_service import register_user, login_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    try:
        user = await register_user(data, db)
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenOut)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    try:
        token = await login_user(data.login, data.password, db)
        return {"access_token": token}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

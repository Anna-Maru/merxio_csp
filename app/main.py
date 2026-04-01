from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.products import router as products_router
from app.api.cart import router as cart_router
from app.api.orders import router as orders_router
from app.api.analytics import router as analytics_router
from fastapi.staticfiles import StaticFiles

app = FastAPI(
    title="Shop API",
    description="E-commerce API с аналитикой продаж",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(products_router)
app.include_router(cart_router)
app.include_router(orders_router)
app.include_router(analytics_router)

app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "message": "Shop API is running"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}

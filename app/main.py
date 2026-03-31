from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "message": "Shop API is running"}


@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok"}

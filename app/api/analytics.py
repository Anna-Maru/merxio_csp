from datetime import datetime
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_admin_user
from app.db.base import get_db
from app.models.user import User
from app.services.analytics_service import (
    get_summary, get_top_products,
    get_sales_by_category, get_sales_dynamics, get_new_users,
)
from app.services.export_service import export_xlsx, export_pdf

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
async def summary(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    return await get_summary(db, date_from, date_to)


@router.get("/top-products")
async def top_products(
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    return await get_top_products(db, limit)


@router.get("/categories")
async def categories(
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    return await get_sales_by_category(db)


@router.get("/dynamics")
async def dynamics(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    group_by: str = Query("day"),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    return await get_sales_dynamics(db, date_from, date_to, group_by)


@router.get("/users")
async def new_users(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    return await get_new_users(db, date_from, date_to)


@router.get("/export/xlsx")
async def export_to_xlsx(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    summary = await get_summary(db, date_from, date_to)
    top = await get_top_products(db)
    cats = await get_sales_by_category(db)
    dynamics = await get_sales_dynamics(db, date_from, date_to)

    buffer = export_xlsx(summary, top, cats, dynamics)
    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=report.xlsx"},
    )


@router.get("/export/pdf")
async def export_to_pdf(
    date_from: datetime | None = Query(None),
    date_to: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_admin_user),
):
    summary = await get_summary(db, date_from, date_to)
    top = await get_top_products(db)
    cats = await get_sales_by_category(db)

    buffer = export_pdf(summary, top, cats)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=report.pdf"},
    )

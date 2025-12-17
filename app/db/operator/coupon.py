from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from uuid import UUID

from sqlalchemy.orm import joinedload
from app.db.models.coupon import Coupon


async def get_coupon_by_id(db: AsyncSession, coupon_id: UUID):
    stmt = select(Coupon).where(Coupon.coupon_id == coupon_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_active_admin_coupons(db: AsyncSession):
    stmt = (
        select(Coupon)
        .where(Coupon.staff == None)  
        .where(Coupon.start_date <= date.today())
        .where(
            (Coupon.end_date.is_(None)) |
            (Coupon.end_date > date.today())
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_active_bookstore_coupons(db: AsyncSession):
    stmt = (
        select(Coupon)
        .where(Coupon.staff != None)  
        .where(Coupon.start_date <= date.today())
        .where(
            (Coupon.end_date.is_(None)) |
            (Coupon.end_date > date.today())
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()

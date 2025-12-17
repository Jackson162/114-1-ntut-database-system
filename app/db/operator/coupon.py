from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.db.models.coupon import Coupon


async def get_coupon_by_id(db: AsyncSession, coupon_id: UUID):
    query = select(Coupon).where(Coupon.coupon_id == coupon_id).options(joinedload(Coupon.staff))
    result = await db.execute(query)
    return result.scalars().one_or_none()

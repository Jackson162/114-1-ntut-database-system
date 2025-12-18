from datetime import date
from typing import Optional, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import joinedload
from app.db.models.coupon import Coupon
from app.enum.coupon import CouponType
from app.enum.user import UserRole


async def get_coupon_by_id(db: AsyncSession, coupon_id: UUID):
    query = select(Coupon).where(Coupon.coupon_id == coupon_id).options(joinedload(Coupon.staff))
    result = await db.execute(query)
    return result.scalars().one_or_none()


async def create_coupon(
    db: AsyncSession,
    account: str,
    name: str,
    type: CouponType,
    discount_percentage: float,
    start_date: date,
    end_date: Optional[date],
    role: UserRole,
):
    values = {
        "name": name,
        "type": type,
        "discount_percentage": discount_percentage,
        "start_date": start_date,
        "end_date": end_date,
    }

    if role == UserRole.ADMIN.value:
        values["admin_account"] = account
    elif role == UserRole.STAFF.value:
        values["staff_account"] = account

    query = insert(Coupon).values(values).returning(Coupon)

    result = await db.execute(query)
    return result.scalars().one()


async def get_coupon_by_accounts(db: AsyncSession, accounts: List[str], role: UserRole):

    query = select(Coupon).where(Coupon.admin_account.in_(accounts))

    if role == UserRole.STAFF.value:
        query = select(Coupon).where(Coupon.staff_account.in_(accounts))

    result = await db.execute(query)
    return result.scalars().all()

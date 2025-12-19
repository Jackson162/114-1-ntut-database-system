from typing import List, Optional
from datetime import date
from uuid import UUID


from sqlalchemy import select, insert, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.coupon import Coupon
from app.enum.coupon import CouponType
from app.enum.user import UserRole
from app.db.models.staff import Staff


async def get_coupon_by_id(db: AsyncSession, coupon_id: UUID):
    stmt = select(Coupon).where(Coupon.coupon_id == coupon_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_active_admin_coupons(db: AsyncSession):
    stmt = (
        select(Coupon)
        .where(Coupon.admin_account.is_not(None))
        .where(Coupon.start_date <= date.today())
        .where((Coupon.end_date.is_(None)) | (Coupon.end_date > date.today()))
        .options(joinedload(Coupon.admin))
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_active_bookstore_coupons(db: AsyncSession):
    stmt = (
        select(Coupon)
        .where(Coupon.staff_account.is_not(None))
        .where(Coupon.start_date <= date.today())
        .where((Coupon.end_date.is_(None)) | (Coupon.end_date > date.today()))
        .options(joinedload(Coupon.staff).options(joinedload(Staff.bookstore)))
    )
    result = await db.execute(stmt)
    return result.scalars().all()


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

    if role == UserRole.ADMIN:
        query = (
            select(Coupon)
            .where(Coupon.admin_account.in_(accounts))
            .options(joinedload(Coupon.admin))
        )
    elif role == UserRole.STAFF:
        query = (
            select(Coupon)
            .where(Coupon.staff_account.in_(accounts))
            .options(joinedload(Coupon.staff))
        )
    else:
        return []

    result = await db.execute(query)
    return result.scalars().all()


async def delete_coupon(db: AsyncSession, coupon_id: UUID):
    query = delete(Coupon).where(Coupon.coupon_id == coupon_id).returning(Coupon)
    result = await db.execute(query)
    return result.scalars().one_or_none()

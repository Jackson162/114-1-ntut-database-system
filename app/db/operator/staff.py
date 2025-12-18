from typing import Optional, Dict, Any
from uuid import UUID
from app.db.models.staff import Staff
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, delete


async def get_staff_by_account(db: AsyncSession, account: str):
    query = select(Staff).where(Staff.account == account)
    result = await db.execute(query)
    return result.scalars().one()


async def create_staff(
    db: AsyncSession,
    account: str,
    name: str,
    password: str,
    bookstore_id: Optional[UUID] = None,
    auto_commit: bool = False,
):
    insert_values: Dict[str, Any] = {
        "account": account,
        "name": name,
        "password": password,
    }

    if bookstore_id:
        insert_values["bookstore_id"] = bookstore_id

    query = insert(Staff).values(insert_values)

    await db.execute(query)

    if auto_commit:
        await db.commit()


async def update_staff(
    db: AsyncSession,
    account: str,
    name: Optional[str] = None,
    password: Optional[str] = None,
    bookstore_id: Optional[UUID] = None,
    auto_commit: Optional[bool] = False,
):
    query = select(Staff).where(Staff.account == account)
    result = await db.execute(query)
    staff = result.scalars().one()

    if name is not None:
        staff.name = name

    if password is not None:
        staff.password = password

    if bookstore_id is not None:
        staff.bookstore_id = bookstore_id

    db.add(staff)
    await db.flush()

    if auto_commit:
        await db.commit()

    return staff


async def get_staffs_by_bookstore_id(db: AsyncSession, bookstore_id: UUID):
    query = select(Staff).where(Staff.bookstore_id == bookstore_id)
    result = await db.execute(query)
    return result.scalars().all()

async def delete_staff(db: AsyncSession, account: str):
    """刪除員工"""
    query = delete(Staff).where(Staff.account == account)
    await db.execute(query)
    await db.commit()

from typing import Optional, Dict, Any
from uuid import UUID
from app.db.models.staff import Staff
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select


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

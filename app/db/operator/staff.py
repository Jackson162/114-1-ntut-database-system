from typing import Optional, Dict, Any
from app.db.models.staff import Staff
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from uuid import UUID


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

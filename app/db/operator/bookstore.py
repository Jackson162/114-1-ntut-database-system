from typing import Optional, Dict, Any
from uuid import UUID
from app.db.models.staff import Staff
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select
from app.db.models.bookstore import Bookstore


async def create_bookstore(
    db: AsyncSession,
    name: str,
    phone_number: str,
    email: str,
    address: str,
    shipping_fee: int,
    auto_commit: bool = False,
):
    query = (
        insert(Bookstore)
        .values(
            name=name,
            phone_number=phone_number,
            email=email,
            address=address,
            shipping_fee=shipping_fee,
        )
        .returning(Bookstore)
    )

    result = await db.execute(query)

    if auto_commit:
        await db.commit()

    return result.scalar_one()

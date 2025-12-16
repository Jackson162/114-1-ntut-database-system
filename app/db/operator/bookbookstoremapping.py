from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update
from app.db.models.book_bookstore_mapping import BookBookstoreMapping


async def get_book_mapping(
    db: AsyncSession, book_id: UUID, bookstore_id: UUID
) -> Optional[BookBookstoreMapping]:
    stmt = select(BookBookstoreMapping).where(
        and_(
            BookBookstoreMapping.book_id == book_id,
            BookBookstoreMapping.bookstore_id == bookstore_id,
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()


# 扣除庫存
async def decrease_stock(db: AsyncSession, mapping_id: UUID, quantity: int):
    # 原本數量 - 購買數量
    stmt = (
        update(BookBookstoreMapping)
        .where(BookBookstoreMapping.book_bookstore_mapping_id == mapping_id)
        .values(store_quantity=BookBookstoreMapping.store_quantity - quantity)
    )
    await db.execute(stmt)

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.db.models.book_bookstore_mapping import BookBookstoreMapping


# 扣除庫存
async def decrease_stock(db: AsyncSession, mapping_id: UUID, quantity: int):
    # 原本數量 - 購買數量
    stmt = (
        update(BookBookstoreMapping)
        .where(BookBookstoreMapping.book_bookstore_mapping_id == mapping_id)
        .values(store_quantity=BookBookstoreMapping.store_quantity - quantity)
    )
    await db.execute(stmt)

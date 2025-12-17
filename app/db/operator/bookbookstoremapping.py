from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, insert
from app.db.models.book_bookstore_mapping import BookBookstoreMapping


async def get_book_mapping_by_mapping_id(
    db: AsyncSession, book_bookstore_mapping_id: UUID
) -> Optional[BookBookstoreMapping]:
    stmt = select(BookBookstoreMapping).where(
        BookBookstoreMapping.book_bookstore_mapping_id == book_bookstore_mapping_id
    )
    result = await db.execute(stmt)
    return result.scalars().one_or_none()


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


async def create_book_bookstore_mapping(
    db: AsyncSession, book_id: UUID, bookstore_id: UUID, price: int, store_quantity: int
):
    query = (
        insert(BookBookstoreMapping)
        .values(
            book_id=book_id, bookstore_id=bookstore_id, price=price, store_quantity=store_quantity
        )
        .returning(BookBookstoreMapping.book_bookstore_mapping_id)
    )

    result = await db.execute(query)

    return result.scalar_one()


async def update_book_bookstore_mapping(
    db: AsyncSession,
    book_bookstore_mapping_id: UUID,
    price: Optional[int] = None,
    store_quantity: Optional[int] = None,
):
    values = {}

    if price is not None:
        values["price"] = price

    if store_quantity is not None:
        values["store_quantity"] = store_quantity

    query = (
        update(BookBookstoreMapping)
        .values(values)
        .where(BookBookstoreMapping.book_bookstore_mapping_id == book_bookstore_mapping_id)
        .returning(BookBookstoreMapping.book_bookstore_mapping_id)
    )

    result = await db.execute(query)

    return result.scalar_one()

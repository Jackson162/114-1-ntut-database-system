from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, insert, delete, or_
from app.db.models.book_bookstore_mapping import BookBookstoreMapping
from app.db.models.bookstore import Bookstore
from app.db.models.book import Book


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


async def delete_book_bookstore_mapping(
    db: AsyncSession,
    book_bookstore_mapping_id: UUID,
):
    query = (
        delete(BookBookstoreMapping)
        .where(BookBookstoreMapping.book_bookstore_mapping_id == book_bookstore_mapping_id)
        .returning(BookBookstoreMapping)
    )

    result = await db.execute(query)

    return result.scalars().one()


async def search_books_with_mappings(db: AsyncSession, keyword: str):
    """
    搜尋書籍並回傳所有書店的販售資訊 (Book + Mapping)
    """
    stmt = (
        select(Book, BookBookstoreMapping)
        .join(BookBookstoreMapping, Book.book_id == BookBookstoreMapping.book_id)
        .where(or_(Book.title.ilike(f"%{keyword}%"), Book.author.ilike(f"%{keyword}%")))
        .order_by(BookBookstoreMapping.price.asc())  # 搜尋結果依價格排序
    )
    result = await db.execute(stmt)
    return result.all()  # 回傳 list of (Book, BookBookstoreMapping) tuples


async def get_new_arrivals_with_mappings(db: AsyncSession, limit: int = 10):
    """
    取得最新上架書籍的所有書店販售資訊
    """
    stmt = (
        select(Book, BookBookstoreMapping)
        .join(BookBookstoreMapping, Book.book_id == BookBookstoreMapping.book_id)
        .order_by(Book.publish_date.desc(), BookBookstoreMapping.price.asc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()  # 回傳 list of (Book, BookBookstoreMapping) tuples


async def get_book_display_data(db: AsyncSession, book):
    # 查詢該書的 mapping，依價格低到高排序，取第一筆 (最低價)
    stmt = (
        select(BookBookstoreMapping)
        .where(BookBookstoreMapping.book_id == book.book_id)
        .order_by(BookBookstoreMapping.price.asc())
        .limit(1)
    )
    result = await db.execute(stmt)
    mapping = result.scalars().first()

    return {
        "book_id": book.book_id,
        "title": book.title,
        "author": book.author,
        "image_url": "https://placehold.co/180x120",  # Placeholder image
        "price": mapping.price if mapping else "N/A",
        "bookstore_id": mapping.bookstore_id if mapping else None,  # 關鍵：加入 bookstore_id
    }


async def search_books_with_bookstore_details(db: AsyncSession, keyword: str):
    """
    搜尋書籍，並回傳 (Book, Mapping, Bookstore) 的組合。
    這樣可以顯示同一本書在不同書店的價格與資訊。
    """
    stmt = (
        select(Book, BookBookstoreMapping, Bookstore)
        .join(BookBookstoreMapping, Book.book_id == BookBookstoreMapping.book_id)
        .join(Bookstore, BookBookstoreMapping.bookstore_id == Bookstore.bookstore_id)
        .where(or_(Book.title.ilike(f"%{keyword}%"), Book.author.ilike(f"%{keyword}%")))
        .order_by(Bookstore.name, Book.title)  # 依書店排序，方便前端分組
    )
    result = await db.execute(stmt)
    return result.all()


async def get_new_arrivals_with_bookstore_details(db: AsyncSession, limit: int = 20):
    """
    取得最新上架書籍，並包含書店資訊。
    """
    stmt = (
        select(Book, BookBookstoreMapping, Bookstore)
        .join(BookBookstoreMapping, Book.book_id == BookBookstoreMapping.book_id)
        .join(Bookstore, BookBookstoreMapping.bookstore_id == Bookstore.bookstore_id)
        .order_by(Book.publish_date.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.all()

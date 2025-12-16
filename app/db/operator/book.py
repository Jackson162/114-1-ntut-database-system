from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, func, or_

from app.db.models.book_bookstore_mapping import BookBookstoreMapping
from app.db.models.book import Book


async def list_books_by_bookstore_id(db: AsyncSession, bookstore_id: UUID):
    query = (
        select(
            Book.book_id,
            Book.title,
            Book.author,
            Book.publisher,
            Book.isbn,
            Book.category,
            Book.publish_date,
            BookBookstoreMapping.price,
            BookBookstoreMapping.store_quantity,
            BookBookstoreMapping.book_bookstore_mapping_id,
            BookBookstoreMapping.bookstore_id,
        )
        .join(BookBookstoreMapping, BookBookstoreMapping.book_id == Book.book_id)
        .where(BookBookstoreMapping.bookstore_id == bookstore_id)
    )

    result = await db.execute(query)
    return list(result.all())


async def get_all_categories(db: AsyncSession):
    stmt = select(Book.category).distinct()
    result = await db.execute(stmt)
    return [row[0] for row in result.all() if row[0]]


async def get_new_arrivals(db: AsyncSession, limit: int = 5):
    stmt = (
        select(Book)
        .order_by(Book.publish_date.desc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_all_books(db: AsyncSession):
    stmt = select(Book)
    result = await db.execute(stmt)
    return result.scalars().all()


async def search_books(db: AsyncSession, keyword: str):
    stmt = select(Book).where(
        or_(
            Book.title.ilike(f"%{keyword}%"),
            Book.author.ilike(f"%{keyword}%")
        )
    )
    result = await db.execute(stmt)
    return result.scalars().all()
    
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
        "image_url": "https://placehold.co/180x120", # Placeholder image
        "min_price": mapping.price if mapping else "N/A",
        "bookstore_id": mapping.bookstore_id if mapping else None # 關鍵：加入 bookstore_id
    }

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select

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

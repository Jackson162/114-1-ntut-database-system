from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload, joinedload

from app.db.models.book import Book
from app.db.models.book_bookstore_mapping import BookBookstoreMapping


async def get_books(
    db: AsyncSession,
    keyword: Optional[str] = None,
    category: Optional[str] = None,
) -> List[Book]:
    """
    Search books by keyword (title or author) or category.
    """
    query = select(Book)

    if keyword:
        # Simple fuzzy search on title or author
        kw = f"%{keyword}%"
        query = query.where(or_(Book.title.ilike(kw), Book.author.ilike(kw)))

    if category:
        query = query.where(Book.category == category)
    
    # Order by title by default
    query = query.order_by(Book.title)

    result = await db.execute(query)
    return result.scalars().all()


async def get_book_with_details(db: AsyncSession, book_id: UUID) -> Optional[Book]:
    """
    Get a single book with all its bookstore mappings (prices and stock).
    """
    query = (
        select(Book)
        .where(Book.book_id == book_id)
        .options(
            selectinload(Book.book_bookstore_mapping).joinedload(BookBookstoreMapping.bookstore)
        )
    )
    
    result = await db.execute(query)
    return result.scalars().one_or_none()
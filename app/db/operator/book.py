from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.book import Book


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

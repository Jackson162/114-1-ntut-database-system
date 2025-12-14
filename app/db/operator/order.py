from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload
from app.db.models.order import Order
from app.db.models.order_item import OrderItem
from app.db.models.book_bookstore_mapping import BookBookstoreMapping
from app.db.models.book import Book


async def get_orders_by_customer_account(db: AsyncSession, customer_account: str):

    options = (
        # 1. Order.order_items (TO-MANY collection) -> CORRECT: selectinload
        selectinload(Order.order_items).options(
            # 2. OrderItem.book_bookstore_mapping (TO-ONE object) -> CORRECTED: joinedload
            joinedload(OrderItem.book_bookstore_mapping).options(
                # 3. BookBookstoreMapping.book (TO-ONE object) -> CORRECT: joinedload
                joinedload(BookBookstoreMapping.book),
                # 4. BookBookstoreMapping.bookstore (TO-ONE object) -> CORRECT: joinedload
                joinedload(BookBookstoreMapping.bookstore),
            )
        )
    )
    query = select(Order).where(Order.customer_account == customer_account).options(options)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_orders_by_bookstore_id(db: AsyncSession, bookstore_id: UUID):

    query = (
        select(OrderItem.order_id)
        .join(
            BookBookstoreMapping,
            OrderItem.book_bookstore_mapping_id == BookBookstoreMapping.book_bookstore_mapping_id,
        )
        .where(BookBookstoreMapping.bookstore_id == bookstore_id)
        .group_by(OrderItem.order_id)
    )

    result = await db.execute(query)
    order_ids = list(result.scalars().all())

    options = (
        # 1. Order.order_items (TO-MANY collection) -> CORRECT: selectinload
        selectinload(Order.order_items).options(
            # 2. OrderItem.book_bookstore_mapping (TO-ONE object) -> CORRECTED: joinedload
            joinedload(OrderItem.book_bookstore_mapping).options(
                # 3. BookBookstoreMapping.book (TO-ONE object) -> CORRECT: joinedload
                joinedload(BookBookstoreMapping.book),
                # 4. BookBookstoreMapping.bookstore (TO-ONE object) -> CORRECT: joinedload
                joinedload(BookBookstoreMapping.bookstore),
            )
        )
    )

    query = select(Order).where(Order.order_id.in_(order_ids)).options(options)

    result = await db.execute(query)
    return list(result.scalars().all())

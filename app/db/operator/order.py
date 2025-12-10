from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.orm import selectinload, joinedload
from app.db.models.order import Order
from app.db.models.order_item import OrderItem
from app.db.models.book_bookstore_mapping import BookBookstoreMapping
from uuid import UUID
from datetime import date


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


# 建立訂單
async def create_order(
    db: AsyncSession,
    account: str,
    customer_name: str,
    customer_phone: str,
    address: str,
    total_price: int,
    shipping_fee: int,
    recipient_name: str,
    customer_email: str | None = None,
) -> Order:
    # 這裡 status 先預設為 "Pending" 或 "Processing"
    stmt = (
        insert(Order)
        .values(
            customer_account=account,
            order_time=date.today(),
            customer_name=customer_name,
            customer_phone_number=customer_phone,
            customer_email=customer_email,
            shipping_address=address,
            total_price=total_price,
            shipping_fee=shipping_fee,
            recipient_name=recipient_name,
            status="pending",
        )
        .returning(Order)
    )

    result = await db.execute(stmt)
    return result.scalars().one()


# 2. 訂單細項
async def create_order_item(
    db: AsyncSession, order_id: UUID, mapping_id: UUID, quantity: int, price: int
):
    stmt = insert(OrderItem).values(
        order_id=order_id, book_bookstore_mapping_id=mapping_id, quantity=quantity, price=price
    )
    await db.execute(stmt)

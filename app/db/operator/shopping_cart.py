from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, and_, delete
from sqlalchemy.orm import selectinload

# from sqlalchemy.orm import selectinload

from app.db.models.shopping_cart import ShoppingCart
from app.db.models.cart_item import CartItem
from app.db.models.book_bookstore_mapping import BookBookstoreMapping


# 取得cart
async def get_cart_by_account(db: AsyncSession, account: str) -> Optional[ShoppingCart]:
    """
    stmt = select(ShoppingCart).where(ShoppingCart.customer_account == account)
    result = await db.execute(stmt)
    return result.scalars().first()
    """
    stmt = (
        select(ShoppingCart)
        .where(ShoppingCart.customer_account == account)
        .options(
            selectinload(ShoppingCart.cart_items).options(
                selectinload(CartItem.book_bookstore_mapping).options(
                    selectinload(BookBookstoreMapping.bookstore),
                    selectinload(BookBookstoreMapping.book),
                )
            )
        )
    )
    result = await db.execute(stmt)
    return result.scalars().first()


# 建立cart
async def create_cart(db: AsyncSession, account: str) -> ShoppingCart:
    stmt = insert(ShoppingCart).values(customer_account=account).returning(ShoppingCart)
    result = await db.execute(stmt)
    return result.scalars().one()


# 取得cart的商品
async def get_cart_item(db: AsyncSession, cart_id: UUID, mapping_id: UUID) -> Optional[CartItem]:
    stmt = select(CartItem).where(
        and_(CartItem.cart_id == cart_id, CartItem.book_bookstore_mapping_id == mapping_id)
    )
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_cart_item_by_item_id(db: AsyncSession, cart_item_id: UUID):
    stmt = select(CartItem).where(CartItem.cart_item_id == cart_item_id)
    result = await db.execute(stmt)
    return result.scalars().first()


# 數量更新
async def update_cart_item_quantity(db: AsyncSession, cart_item_id: UUID, quantity: int):
    stmt = update(CartItem).where(CartItem.cart_item_id == cart_item_id).values(quantity=quantity)
    await db.execute(stmt)


# 新增商品
async def create_cart_item(db: AsyncSession, cart_id: UUID, mapping_id: UUID, quantity: int):
    stmt = insert(CartItem).values(
        cart_id=cart_id, book_bookstore_mapping_id=mapping_id, quantity=quantity
    )
    await db.execute(stmt)


# 清空購物車項目
async def clear_cart_items(db: AsyncSession, cart_id: UUID):
    stmt = delete(CartItem).where(CartItem.cart_id == cart_id)
    await db.execute(stmt)


async def delete_cart_item_by_item_id(db: AsyncSession, cart_item_id: UUID):
    query = delete(CartItem).where(CartItem.cart_item_id == cart_item_id)
    await db.execute(query)

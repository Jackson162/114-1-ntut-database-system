from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, and_

# from sqlalchemy.orm import selectinload

from app.db.models.shopping_cart import ShoppingCart
from app.db.models.cart_item import CartItem
from app.db.models.book_bookstore_mapping import BookBookstoreMapping


async def add_item_to_cart(
    db: AsyncSession, customer_account: str, book_id: UUID, price: int, quantity: int
):
    # 1. 先確認該使用者有沒有購物車
    stmt = select(ShoppingCart).where(ShoppingCart.customer_account == customer_account)
    result = await db.execute(stmt)
    cart = result.scalars().first()

    # 如果沒有購物車，就幫他建立一個
    if not cart:
        stmt_create_cart = (
            insert(ShoppingCart).values(customer_account=customer_account).returning(ShoppingCart)
        )
        result_create = await db.execute(stmt_create_cart)
        cart = result_create.scalars().one()
        # 注意：這裡還沒 commit，最後一起 commit

    # 2. 找出對應的 Mapping ID
    # 因為系統設計是 BookBookstoreMapping 決定價格，所以要用 book_id + price 反查
    stmt_mapping = select(BookBookstoreMapping).where(
        and_(BookBookstoreMapping.book_id == book_id, BookBookstoreMapping.price == price)
    )
    result_mapping = await db.execute(stmt_mapping)
    mapping = result_mapping.scalars().first()

    if not mapping:
        raise Exception("找不到該價格的書籍商品 (Book not found with the given price)")

    # 3. 檢查購物車內是否已經有這個商品
    stmt_item = select(CartItem).where(
        and_(
            CartItem.cart_id == cart.cart_id,
            CartItem.book_bookstore_mapping_id == mapping.book_bookstore_mapping_id,
        )
    )
    result_item = await db.execute(stmt_item)
    existing_item = result_item.scalars().first()

    if existing_item:
        # A. 如果已存在，就更新數量 (原本數量 + 新增數量)
        stmt_update = (
            update(CartItem)
            .where(CartItem.cart_item_id == existing_item.cart_item_id)
            .values(quantity=existing_item.quantity + quantity)
        )
        await db.execute(stmt_update)
    else:
        # B. 如果不存在，就新增一筆
        stmt_insert = insert(CartItem).values(
            cart_id=cart.cart_id,
            book_bookstore_mapping_id=mapping.book_bookstore_mapping_id,
            quantity=quantity,
        )
        await db.execute(stmt_insert)

    # 4. 全部完成後，提交變更
    await db.commit()
    return True

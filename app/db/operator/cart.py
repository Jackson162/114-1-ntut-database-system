from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, literal
from app.db.models.shopping_cart import ShoppingCart
from app.db.models.cart_item import CartItem
from app.db.models.book import Book
from app.db.models.bookstore import Bookstore
from app.db.models.book_bookstore_mapping import BookBookstoreMapping


async def get_cart_item_count(
    db: AsyncSession,
    customer_account: str,
) -> int:
    stmt = (
        select(func.coalesce(func.sum(CartItem.quantity), 0))
        .join(
            ShoppingCart,
            ShoppingCart.cart_id == CartItem.cart_id,
        )
        .where(ShoppingCart.customer_account == customer_account)
    )

    result = await db.execute(stmt)
    return result.scalar_one()


async def get_cart_details(
    db: AsyncSession,
    customer_account: str,
):

    stmt = (
        select(
            CartItem.cart_item_id,
            CartItem.quantity,
            Book.book_id,
            Book.title,
            Book.author,
            # 使用 literal 處理圖片預設值
            (
                Book.image_url
                if hasattr(Book, "image_url")
                else literal("https://placehold.co/120x160").label("image_url")
            ),
            Bookstore.bookstore_id,
            Bookstore.name,
            BookBookstoreMapping.price,
            BookBookstoreMapping.store_quantity,
        )
        .join(ShoppingCart, ShoppingCart.cart_id == CartItem.cart_id)
        .join(
            BookBookstoreMapping,
            BookBookstoreMapping.book_bookstore_mapping_id == CartItem.book_bookstore_mapping_id,
        )
        .join(Book, Book.book_id == BookBookstoreMapping.book_id)
        .join(Bookstore, Bookstore.bookstore_id == BookBookstoreMapping.bookstore_id)
        .where(ShoppingCart.customer_account == customer_account)
    )

    result = await db.execute(stmt)
    return result.all()

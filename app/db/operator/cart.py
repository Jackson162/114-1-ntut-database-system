from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.db.models.shopping_cart import ShoppingCart
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.cart_item import CartItem

async def create_shopping_cart(
    db: AsyncSession,
    customer_account: str,
    auto_commit: bool = False,
):
    query = insert(ShoppingCart).values(customer_account=customer_account).returning(ShoppingCart)

    result = await db.execute(query)

    if auto_commit:
        await db.commit()

    return result.scalar_one()

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
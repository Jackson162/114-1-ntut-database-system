from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.db.models.shopping_cart import ShoppingCart


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

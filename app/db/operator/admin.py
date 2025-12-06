from app.db.models.admin import Admin
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select


async def get_admin_by_account(db: AsyncSession, account: str):
    query = select(Admin).where(Admin.account == account)
    result = await db.execute(query)
    return result.scalars().one()


async def create_admin(
    db: AsyncSession,
    account: str,
    name: str,
    password: str,
    auto_commit: bool = False,
):
    insert_values = {
        "account": account,
        "name": name,
        "password": password,
    }

    query = insert(Admin).values(insert_values)

    await db.execute(query)

    if auto_commit:
        await db.commit()

from typing import Optional
from app.db.models.customer import Customer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select


async def get_customer_by_account(db: AsyncSession, account: str):
    query = select(Customer).where(Customer.account == account)
    result = await db.execute(query)
    return result.scalars().one()


async def create_customer(
    db: AsyncSession,
    account: str,
    name: str,
    password: str,
    phone_number: str,
    email: Optional[str] = None,
    address: Optional[str] = None,
    auto_commit: bool = False,
):
    insert_values = {
        "account": account,
        "name": name,
        "password": password,
        "phone_number": phone_number,
        "email": email,
        "address": address,
    }

    if email:
        insert_values["email"] = email

    if address:
        insert_values["address"] = address

    query = insert(Customer).values(insert_values)

    await db.execute(query)

    if auto_commit:
        await db.commit()

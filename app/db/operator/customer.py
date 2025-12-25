from typing import Optional
from app.db.models.customer import Customer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import select, update, delete 


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

async def get_all_customers(db: AsyncSession) -> list[Customer]:
    """取得所有使用者列表"""
    query = select(Customer).order_by(Customer.account)
    result = await db.execute(query)
    return result.scalars().all()

async def update_customer_info(db: AsyncSession, account: str, name: str, email: str):
    """更新使用者姓名與 Email"""
    query = (
        update(Customer)
        .where(Customer.account == account)
        .values(name=name, email=email)
    )
    await db.execute(query)
    await db.commit()

async def delete_customer(db: AsyncSession, account: str):
    """刪除使用者"""
    query = delete(Customer).where(Customer.account == account)
    await db.execute(query)
    await db.commit()

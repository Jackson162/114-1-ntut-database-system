from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Form, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.db_session import get_db_session
from enum.user import UserRole
from app.db.operator.customer import create_customer
from app.db.operator.staff import create_staff

from app.util.auth import hash_password
from app.router.template.index import templates

router = APIRouter()


@router.post("/register")
async def register(
    role: Annotated[str, Form()],
    name: Annotated[str, Form()],
    password: Annotated[str, Form()],
    account: Annotated[str, Form()],
    phone_number: Annotated[Optional[str], Form()],
    email: Annotated[Optional[str], Form()],
    address: Annotated[Optional[str], Form()],
    db: AsyncSession = Depends(get_db_session),
):
    try:
        hashed_password = hash_password(password)
        if role == UserRole.CUSTOMER.value and phone_number:
            await create_customer(
                name=name,
                password=hashed_password,
                account=account,
                phone_number=phone_number,
                email=email,
                address=address,
                db=db,
            )
        elif role == UserRole.STAFF.value:
            await create_staff(name=name, password=hashed_password, account=account, db=db)
    except Exception as err:
        context = {
            "register_error": repr(err),
        }
        return templates.TemplateResponse(
            "register.jinja", context, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    context = {
        "register_succeeded": True,
    }
    return templates.TemplateResponse("login.jinja", context, status_code=status.HTTP_200_OK)

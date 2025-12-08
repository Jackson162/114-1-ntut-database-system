from typing import Tuple, Annotated
from fastapi import APIRouter, Depends, Request, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.staff import Staff
from app.db.operator.bookstore import create_bookstore
from app.db.operator.staff import update_staff
from app.util.auth import JwtPayload

router = APIRouter()

validate_staff_token = validate_token_by_role(UserRole.STAFF)


@router.post("/bookstores/create", response_class=RedirectResponse)
async def create_staff_bookstore(
    request: Request,
    name: Annotated[str, Form()],
    phone_number: Annotated[str, Form()],
    email: Annotated[str, Form()],
    address: Annotated[str, Form()],
    shipping_fee: Annotated[int, Form()],
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data

    try:
        if staff.bookstore_id is not None:
            raise Exception()

        bookstore = await create_bookstore(
            db=db,
            name=name,
            phone_number=phone_number,
            email=email,
            address=address,
            shipping_fee=shipping_fee,
        )

        await update_staff(db=db, account=staff.account, bookstore_id=bookstore.bookstore_id)
        redirect_url = "/frontend/staffs/bookstores"
        await db.commit()
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as err:
        await db.rollback()
        redirect_url = f"/frontend/staffs/bookstores?create_staff_bookstore_error={repr(err)}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

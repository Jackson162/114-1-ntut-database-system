from typing import Tuple, Annotated, Optional
from uuid import UUID
from datetime import date

from fastapi import APIRouter, Depends, Request, status, Form
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.enum.order import OrderStatus
from app.enum.coupon import CouponType
from app.db.models.staff import Staff
from app.db.operator.bookstore import create_bookstore
from app.db.operator.staff import update_staff
from app.db.operator.order import update_order
from app.db.operator.book import create_book, get_book_by_isbn
from app.db.operator.bookbookstoremapping import (
    get_book_mapping,
    create_book_bookstore_mapping,
    get_book_mapping_by_mapping_id,
    update_book_bookstore_mapping,
    delete_book_bookstore_mapping,
)
from app.db.operator.coupon import create_coupon
from app.util.auth import JwtPayload
from app.logging.logger import get_logger

logger = get_logger()


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

        await db.commit()

        redirect_url = "/frontend/staffs/bookstores"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as err:
        await db.rollback()
        redirect_url = f"/frontend/staffs/bookstores?create_staff_bookstore_error={repr(err)}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/orders/update", response_class=RedirectResponse)
async def update_staff_order(
    request: Request,
    order_id: Annotated[UUID, Form()],
    order_status: Annotated[OrderStatus, Form()],
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        await update_order(db=db, order_id=order_id, order_status=order_status)
        await db.commit()

        redirect_url = "/frontend/staffs/orders"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as err:
        await db.rollback()
        redirect_url = f"/frontend/staffs/orders?update_order_error={repr(err)}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/books/create", response_class=RedirectResponse)
async def create_staff_book(
    request: Request,
    price: Annotated[int, Form()],
    store_quantity: Annotated[int, Form()],
    title: Annotated[str, Form()],
    author: Annotated[str, Form()],
    publisher: Annotated[str, Form()],
    isbn: Annotated[str, Form()],
    category: Annotated[str, Form()],
    publish_date: Annotated[date, Form()],
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data

    try:
        book = await get_book_by_isbn(db=db, isbn=isbn)

        if book is None:
            book = await create_book(
                db=db,
                title=title,
                author=author,
                publisher=publisher,
                isbn=isbn,
                category=category,
                publish_date=publish_date,
            )

        mapping = await get_book_mapping(
            db=db, book_id=book.book_id, bookstore_id=staff.bookstore_id
        )

        if mapping is not None:
            raise Exception(
                f"The book with isbn: {isbn} already exists in the bookstore: {staff.bookstore_id}."
            )

        mapping = await create_book_bookstore_mapping(
            db=db,
            book_id=book.book_id,
            bookstore_id=staff.bookstore_id,
            price=price,
            store_quantity=store_quantity,
        )

        await db.commit()

        redirect_url = "/frontend/staffs/books?create_book_succeeds=true"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as err:
        await db.rollback()
        logger.error(err)
        redirect_url = f"/frontend/staffs/books?create_book_error={repr(err)}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    "/book_bookstore_mappings/{book_bookstore_mapping_id}/update", response_class=RedirectResponse
)
async def update_staff_book_mapping(
    request: Request,
    book_bookstore_mapping_id: UUID,
    price: Annotated[Optional[int], Form()],
    store_quantity: Annotated[Optional[int], Form()],
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data

    try:
        if price is not None and price < 0:
            raise Exception("Unable to set price to negative value!")

        if store_quantity is not None and store_quantity < 0:
            raise Exception("Unable to set store_quantity to negative value!")

        mapping = await get_book_mapping_by_mapping_id(
            db=db, book_bookstore_mapping_id=book_bookstore_mapping_id
        )

        if mapping is None:
            raise Exception("The book does not exist in this bookstore")

        mapping = await update_book_bookstore_mapping(
            db=db,
            book_bookstore_mapping_id=book_bookstore_mapping_id,
            price=price,
            store_quantity=store_quantity,
        )

        await db.commit()

        redirect_url = "/frontend/staffs/books?update_book_succeeds=true"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as err:
        await db.rollback()
        logger.error(err)
        redirect_url = f"/frontend/staffs/books?update_book_error={repr(err)}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post(
    "/book_bookstore_mappings/{book_bookstore_mapping_id}/delete", response_class=RedirectResponse
)
async def delete_staff_book_mapping(
    request: Request,
    book_bookstore_mapping_id: UUID,
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):

    try:
        mapping = await get_book_mapping_by_mapping_id(
            db=db, book_bookstore_mapping_id=book_bookstore_mapping_id
        )

        if mapping is None:
            raise Exception("The book does not exist in this bookstore")

        # check if the mapping is referenced by the cart items or order items

        mapping = await delete_book_bookstore_mapping(
            db=db,
            book_bookstore_mapping_id=book_bookstore_mapping_id,
        )

        await db.commit()

        redirect_url = "/frontend/staffs/books?delete_book_succeeds=true"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as err:
        await db.rollback()
        logger.error(err)
        redirect_url = f"/frontend/staffs/books?delete_book_error={repr(err)}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/coupons/create", response_class=RedirectResponse)
async def create_staff_coupon(
    request: Request,
    name: str,
    type: CouponType,
    discount_percentage: float,
    start_date: date,
    end_date: Optional[date],
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data

    try:
        await create_coupon(
            db=db,
            account=staff.account,
            name=name,
            type=type,
            discount_percentage=discount_percentage,
            start_date=start_date,
            end_date=end_date,
            role=UserRole.STAFF,
        )
        await db.commit()
        redirect_url = "/frontend/staffs/coupons"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as err:
        logger.error(err)
        await db.rollback()
        redirect_url = f"/frontend/staffs/coupons?create_coupon_error={repr(err)}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

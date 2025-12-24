from typing import Tuple, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.enum.order import OrderStatus
from app.enum.coupon import CouponType
from app.db.models.staff import Staff
from app.db.operator.bookstore import get_bookstore_by_id
from app.db.operator.order import get_orders_by_bookstore_id
from app.db.operator.book import list_books_by_bookstore_id
from app.db.operator.staff import get_staffs_by_bookstore_id
from app.db.operator.coupon import get_coupon_by_accounts

from app.util.auth import JwtPayload
from app.router.template.index import templates
from app.router.schema.sqlalchemy import (
    BookstoreSchema,
    OrderSchema,
    OrderItemSchema,
    BookSchema,
    CouponSchema,
    BookWithMappingInfo,
    StaffSchema,
)
from app.logging.logger import get_logger

logger = get_logger()

router = APIRouter()

validate_staff_token = validate_token_by_role(UserRole.STAFF)


@router.get("/bookstores")
async def get_staff_bookstore(
    request: Request,
    create_staff_bookstore_error: Optional[str] = None,
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data

    get_staff_bookstore_error = ""

    try:
        bookstore = await get_bookstore_by_id(db=db, bookstore_id=staff.bookstore_id)
        bookstore_dict = BookstoreSchema.from_orm(bookstore).dict()
    except NoResultFound:
        bookstore_dict = None
    except Exception as err:
        logger.error(err)
        get_staff_bookstore_error = repr(err)
        bookstore_dict = None

    context = {
        "request": request,
        "bookstore": bookstore_dict,
        "get_staff_bookstore_error": get_staff_bookstore_error,
        "create_staff_bookstore_error": None,
    }

    if create_staff_bookstore_error:
        context["create_staff_bookstore_error"] = create_staff_bookstore_error

    return templates.TemplateResponse(
        "/staff/bookstore.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/orders")
async def get_staff_orders(
    request: Request,
    update_order_error: Optional[str] = None,
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data
    list_order_error = None
    try:
        orders = await get_orders_by_bookstore_id(db=db, bookstore_id=staff.bookstore_id)

        order_dicts = []

        for order in orders:
            order_dict = OrderSchema.from_orm(order).dict()
            order_dict["order_items"] = []
            order_dicts.append(order_dict)

            for item in order.order_items:
                item_dict = OrderItemSchema.from_orm(item).dict()
                book = BookSchema.from_orm(item.book_bookstore_mapping.book).dict()
                bookstore = BookstoreSchema.from_orm(item.book_bookstore_mapping.bookstore).dict()
                item_dict["book"] = book
                item_dict["bookstore"] = bookstore

                order_dict["order_items"].append(item_dict)

    except NoResultFound:
        order_dicts = []
    except Exception as err:
        order_dicts = []
        list_order_error = repr(err)

    context = {
        "request": request,
        "staff": staff,
        "orders": order_dicts,
        "order_statuses": [status.value for status in OrderStatus],
        "list_order_error": list_order_error,
        "update_order_error": update_order_error,
    }

    return templates.TemplateResponse(
        "/staff/orders.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/books")
async def get_staff_books(
    request: Request,
    create_book_succeeds: bool = False,
    create_book_error: Optional[str] = None,
    update_book_succeeds: bool = False,
    update_book_error: Optional[str] = None,
    delete_book_succeeds: bool = False,
    delete_book_error: Optional[str] = None,
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data
    list_book_error = None

    try:
        books = await list_books_by_bookstore_id(db=db, bookstore_id=staff.bookstore_id)
        book_dicts = [BookWithMappingInfo.from_orm(book).dict() for book in books]

    except NoResultFound:
        book_dicts = []
    except Exception as err:
        book_dicts = []
        list_book_error = repr(err)

    context = {
        "request": request,
        "staff": staff,
        "books": book_dicts,
        "list_book_error": list_book_error,
        "create_book_succeeds": create_book_succeeds,
        "create_book_error": create_book_error,
        "update_book_succeeds": update_book_succeeds,
        "update_book_error": update_book_error,
        "delete_book_succeeds": delete_book_succeeds,
        "delete_book_error": delete_book_error,
    }

    return templates.TemplateResponse(
        "/staff/books.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/coupons")
async def get_staff_coupons(
    request: Request,
    create_coupon_error: Optional[str] = None,
    delete_coupon_succeeds: bool = False,
    delete_coupon_error: Optional[str] = None,
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data

    list_coupon_error = None
    coupon_dicts = []
    try:
        staffs = await get_staffs_by_bookstore_id(db=db, bookstore_id=staff.bookstore_id)
        staff_accounts = [s.account for s in staffs]

        coupons = await get_coupon_by_accounts(db=db, accounts=staff_accounts, role=UserRole.STAFF)
        coupon_dicts = []

        for c in coupons:
            coupon_dict = CouponSchema.from_orm(c).dict()

            if c.staff:
                coupon_dict["staff"] = StaffSchema.from_orm(c.staff).dict()

            coupon_dicts.append(coupon_dict)

    except Exception as err:
        logger.error(err)
        list_coupon_error = repr(err)

    context = {
        "request": request,
        "coupons": coupon_dicts,
        "create_coupon_error": create_coupon_error,
        "delete_coupon_succeeds": delete_coupon_succeeds,
        "delete_coupon_error": delete_coupon_error,
        "coupon_types": [ct.value for ct in CouponType],
        "list_coupon_error": list_coupon_error,
    }

    return templates.TemplateResponse(
        "/staff/coupons.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/statistics")
async def get_staff_statistics(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    login_data: Tuple[JwtPayload, Staff] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data

    total_revenue = 0
    total_books_sold = 0

    filter_start = None
    filter_end = None
    if start_date:
        try:
            filter_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            pass
    if end_date:
        try:
            filter_end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            pass

    try:
        orders = await get_orders_by_bookstore_id(db=db, bookstore_id=staff.bookstore_id)

        for order in orders:
            if not getattr(order, "order_time", None):
                continue

            order_date = order.order_time
            # Ensure it is a date object (in case driver returns datetime)
            if isinstance(order_date, datetime):
                order_date = order_date.date()

            if filter_start and order_date < filter_start:
                continue
            if filter_end and order_date > filter_end:
                continue

            for item in order.order_items:
                # Ensure we only count items belonging to this staff's bookstore
                if item.book_bookstore_mapping.bookstore_id == staff.bookstore_id:
                    revenue = item.price * item.quantity
                    books_sold = item.quantity

                    total_revenue += revenue
                    total_books_sold += books_sold

    except Exception as err:
        logger.error(f"Error calculating statistics: {err}")

    context = {
        "request": request,
        "staff": staff,
        "start_date": start_date,
        "end_date": end_date,
        "total_revenue": total_revenue,
        "total_books_sold": total_books_sold,
    }

    return templates.TemplateResponse(
        "/staff/statistics.jinja", context=context, status_code=status.HTTP_200_OK
    )

from typing import Optional, Tuple
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.customer import Customer
from app.db.operator.order import get_orders_by_customer_account
from app.db.operator.book import get_books, get_book_with_details
from app.util.auth import JwtPayload, decode_jwt
from app.router.template.index import templates
from app.router.schema.sqlachemy import OrderSchema, OrderItemSchema, BookSchema, BookstoreSchema


router = APIRouter()

validate_customer_token = validate_token_by_role(UserRole.CUSTOMER)


@router.get("/orders")
async def get_customer_orders(
    request: Request,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data
    list_order_error = None
    try:
        orders = await get_orders_by_customer_account(db=db, customer_account=customer.account)

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
        "customer": customer,
        "orders": order_dicts,
        "list_order_error": list_order_error,
    }

    return templates.TemplateResponse(
        "/customer/orders.jinja", context=context, status_code=status.HTTP_200_OK
    )
    
# Helper to get current user optionally (for displaying "Welcome, User" or login button)
async def get_current_user_optional(request: Request) -> Optional[JwtPayload]:
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        return decode_jwt(token)
    except Exception:
        return None

@router.get("/books")
async def list_books_page(
    request: Request,
    keyword: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Page to list all books with search functionality.
    """
    books = await get_books(db=db, keyword=keyword, category=category)
    user = await get_current_user_optional(request)

    context = {
        "request": request,
        "books": books,
        "keyword": keyword or "",
        "user": user,
    }
    
    return templates.TemplateResponse(
        "/customer/list.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/books/{book_id}")
async def book_detail_page(
    request: Request,
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Page to show detailed info of a book and list of bookstores selling it.
    """
    book = await get_book_with_details(db=db, book_id=book_id)
    user = await get_current_user_optional(request)

    error_message = None
    if not book:
        error_message = "Book not found."

    context = {
        "request": request,
        "book": book,
        "user": user,
        "error": error_message
    }

    return templates.TemplateResponse(
        "/customer/detail.jinja", context=context, status_code=status.HTTP_200_OK
    )
    

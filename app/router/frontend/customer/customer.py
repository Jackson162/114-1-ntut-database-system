from typing import Tuple, Optional
from fastapi import APIRouter, Depends, Request, status

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.customer import Customer
from app.db.operator.order import get_orders_by_customer_account
from app.db.operator.book import search_books, get_all_books
from app.util.auth import JwtPayload
from app.router.template.index import templates
from sqlalchemy import select
from app.db.models.book import Book
from app.db.models.bookstore import Bookstore
from app.db.models.book_bookstore_mapping import BookBookstoreMapping

from app.router.schema.sqlalchemy import OrderSchema, OrderItemSchema, BookSchema, BookstoreSchema


router = APIRouter()

validate_customer_token = validate_token_by_role(UserRole.CUSTOMER)


@router.get("/orders")
async def get_customer_orders(
    request: Request,
    checkout_succeeds: bool = False,
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
        "checkout_succeeds": checkout_succeeds,
    }

    return templates.TemplateResponse(
        "/customer/orders.jinja", context=context, status_code=status.HTTP_200_OK
    )


# 結帳畫面
@router.get("/checkout")
async def checkout_page(request: Request, checkout_error: Optional[str] = None):
    context = {"request": request, "checkout_error": checkout_error}

    return templates.TemplateResponse(
        "/customer/checkout.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/books")
async def search_books_page(
    request: Request,
    q: Optional[str] = None,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    # Fetch cart count for the navbar
    cart_count = 0
    try:
        cart_count = await get_cart_item_count(db, customer.account)
    except:
        pass

    # Search logic
    if q:
        books = await search_books(db, q)
    else:
        books = await get_all_books(db)

    # Format books for the template
    books_data = []
    for b in books:
        # Note: In a real scenario, we would join with BookBookstoreMapping to get the actual min_price
        books_data.append(
            {
                "book_id": b.book_id,
                "title": b.title,
                "author": b.author,
                "image_url": "https://placehold.co/180x120",  # Placeholder image
                "min_price": "N/A",  # Placeholder price
            }
        )

    context = {
        "request": request,
        "books": books_data,
        "q": q or "",
        "cart_count": cart_count,
        "customer": customer,
    }

    return templates.TemplateResponse(
        "/customer/books.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/book/{book_id}")  # 修正路徑，現在能匹配 /book/UUID
async def get_book_detail_page(
    book_id: str,
    request: Request,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    # 1. 查詢書籍基本資訊
    result = await db.execute(select(Book).where(Book.book_id == book_id))
    book_obj = result.scalar_one_or_none()

    if not book_obj:
        from fastapi import HTTPException

        raise HTTPException(status_code=404, detail="找不到此書籍")

    # 2. 查詢該書籍在各書店的銷售資訊 (含書店名稱)
    mapping_result = await db.execute(
        select(BookBookstoreMapping, Bookstore.name)
        .join(Bookstore, BookBookstoreMapping.bookstore_id == Bookstore.bookstore_id)
        .where(BookBookstoreMapping.book_id == book_id)
    )

    sales_mappings = []
    for mapping, store_name in mapping_result:
        sales_mappings.append(
            {
                "bookstore_id": mapping.bookstore_id,
                "bookstore_name": store_name,
                "price": mapping.price,
                "store_quantity": mapping.store_quantity,
                "book_bookstore_mapping_id": mapping.book_bookstore_mapping_id,
            }
        )

    # 3. 準備傳給 Jinja 的 context
    context = {
        "request": request,
        "customer": customer,
        "book": book_obj,  # 修正：傳入單數 'book'
        "sales_mappings": sales_mappings,  # 傳入銷售列表
        "cart_count": 0,  # 可根據需求加入購物車數量邏輯
    }

    return templates.TemplateResponse("/customer/books_detail.jinja", context=context)

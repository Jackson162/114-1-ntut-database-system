from typing import Tuple, Optional, Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status, Form
from fastapi.responses import RedirectResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.customer import Customer
from app.db.operator.order import get_orders_by_customer_account
from app.db.operator.coupon import (
    get_active_admin_coupons,
    get_active_bookstore_coupons,
)
from app.util.auth import JwtPayload
from app.router.template.index import templates

from app.router.schema.sqlalchemy import OrderSchema, OrderItemSchema, BookSchema, BookstoreSchema
from app.db.operator.cart import get_cart_item_count, get_cart_details
from app.db.operator.book import get_all_categories
from app.db.operator.bookstore import get_bookstore_by_id
from app.db.operator.bookbookstoremapping import (
    search_books_with_bookstore_details,
    get_new_arrivals_with_bookstore_details,
)


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


@router.get("/books")
async def search_books_redirect(q: Optional[str] = None):
    from fastapi.responses import RedirectResponse

    url = "/frontend/customers/home"
    if q:
        url += f"?q={q}"
    return RedirectResponse(url=url)


def group_results_by_bookstore(rows) -> dict[str, list[dict[str, any]]]:
    """
    輸入 rows: List of (Book, Mapping, Bookstore)
    輸出: {"Bookstore Name": [BookDict, ...]}
    """
    grouped = {}
    for book, mapping, bookstore in rows:
        bs_name = bookstore.name
        if bs_name not in grouped:
            grouped[bs_name] = []

        grouped[bs_name].append(
            {
                "book_id": book.book_id,
                "title": book.title,
                "author": book.author,
                "image_url": "/static/book.png",
                "min_price": mapping.price,  # 前端 book_card 使用 min_price 變數名
                "bookstore_id": bookstore.bookstore_id,
                "bookstore_name": bookstore.name,
            }
        )
    return grouped


@router.get("/home")
async def customer_homepage(
    request: Request,
    q: Optional[str] = None,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):

    _, customer = login_data

    cart_count = 0

    try:
        cart_count = await get_cart_item_count(db, customer.account)
    except Exception:
        pass

    context = {
        "request": request,
        "cart_count": cart_count,
        "q": q or "",
        "grouped_books": {},  # 初始化
        "grouped_new_arrivals": {},  # 初始化
    }

    if q:
        # 搜尋模式：使用新函式並分組
        rows = await search_books_with_bookstore_details(db, q)
        grouped_results = group_results_by_bookstore(rows)

        context.update(
            {
                "is_search_mode": True,
                "grouped_books": grouped_results,
            }
        )
    else:
        # 首頁模式
        categories = []
        try:
            categories = await get_all_categories(db)
        except Exception:
            pass

        # 新書：使用新函式並分組
        new_rows = []
        try:
            new_rows = await get_new_arrivals_with_bookstore_details(db)
        except Exception:
            pass

        grouped_new_arrivals = group_results_by_bookstore(new_rows)

        context.update(
            {
                "is_search_mode": False,
                "categories": categories,
                "grouped_new_arrivals": grouped_new_arrivals,  # 傳遞分組後的資料
                # 暫時留空其他區塊
                "bestsellers": [],
                "promotions": [],
            }
        )

    return templates.TemplateResponse(
        "customer/home.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/carts")
async def view_cart(
    request: Request,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    rows = await get_cart_details(db, customer.account)

    cart_items_data = []
    total_price = 0
    total_items = 0

    for row in rows:
        quantity = row[1]
        price = row[8]
        subtotal = price * quantity
        total_price += subtotal
        total_items += quantity

        cart_items_data.append(
            {
                "cart_item_id": row[0],
                "quantity": quantity,
                "book_id": row[2],
                "title": row[3],
                "author": row[4],
                "image_url": "/static/book.png",
                "bookstore_id": row[6],
                "bookstore_name": row[7],  # 確保有這個欄位供模板 groupby 使用
                "price": price,
                "stock": row[9],
                "subtotal": subtotal,
            }
        )

    context = {
        "request": request,
        "cart_items": cart_items_data,
        "total_price": total_price,
        "total_items": total_items,
        "cart_count": total_items,
        "customer": customer,
    }

    return templates.TemplateResponse(
        "/customer/carts.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/profile")
async def customer_profile_page(
    request: Request,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, customer = login_data

    cart_count = 0
    try:
        cart_count = await get_cart_item_count(db, customer.account)
    except Exception:
        pass

    context = {
        "request": request,
        "customer": customer,
        "cart_count": cart_count,
        "page": "profile",
    }

    return templates.TemplateResponse(
        "/customer/profile.jinja",
        context=context,
        status_code=status.HTTP_200_OK,
    )


@router.post("/profile/update")
async def update_customer_profile(
    name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    phone: Annotated[str, Form()],
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, customer = login_data

    customer.name = name
    customer.email = email
    customer.phone_number = phone

    await db.commit()

    return RedirectResponse(
        url="/frontend/customers/profile",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get("/coupons")
async def customer_coupons_page(
    request: Request,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, customer = login_data

    admin_coupons = await get_active_admin_coupons(db)
    bookstore_coupons = await get_active_bookstore_coupons(db)

    cart_count = 0
    try:
        cart_count = await get_cart_item_count(db, customer.account)
    except Exception:
        pass

    context = {
        "request": request,
        "customer": customer,
        "cart_count": cart_count,
        "page": "coupons",
        "admin_coupons": admin_coupons,
        "bookstore_coupons": bookstore_coupons,
    }

    return templates.TemplateResponse(
        "/customer/profile.jinja",
        context=context,
        status_code=status.HTTP_200_OK,
    )


@router.get("/logout")
async def customer_logout():
    response = RedirectResponse(
        url="/frontend/auth/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.delete_cookie("auth_token", path="/")
    return response


@router.get("/checkout")
async def checkout_page(
    request: Request,
    checkout_error: Optional[str] = None,
    bookstore_id: Optional[UUID] = None,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    if not bookstore_id:
        return RedirectResponse(
            url="/frontend/customers/carts?error=no_bookstore_selected",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    _, customer = login_data

    cart_count = 0
    try:
        cart_count = await get_cart_item_count(db, customer.account)
    except Exception:
        pass

    bookstore = await get_bookstore_by_id(db=db, bookstore_id=bookstore_id)

    if not bookstore:
        return RedirectResponse(
            url="/frontend/customers/carts?error=bookstore_not_found",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    rows = await get_cart_details(db, customer.account)

    checkout_items = []
    items_total_price = 0.0

    for row in rows:
        if str(row[6]) == str(bookstore_id):
            quantity = row[1]
            price = row[8]
            subtotal = price * quantity
            items_total_price += subtotal

            checkout_items.append(
                {
                    "cart_item_id": row[0],
                    "quantity": quantity,
                    "book_id": row[2],
                    "title": row[3],
                    "author": row[4],
                    "image_url": "/static/book.png",
                    "bookstore_id": row[6],
                    "bookstore_name": row[7],
                    "price": price,
                    "stock": row[9],
                    "subtotal": subtotal,
                }
            )

    if not checkout_items:
        return RedirectResponse(
            url=(
                f"/frontend/customers/carts"
                f"?error=no_items_for_this_bookstore&bookstore_id={bookstore_id}"
            ),
            status_code=status.HTTP_303_SEE_OTHER,
        )

    shipping_fee = bookstore.shipping_fee
    grand_total = items_total_price + shipping_fee

    context = {
        "request": request,
        "checkout_error": checkout_error,
        "bookstore_id": bookstore_id,
        "bookstore_name": bookstore.name,
        "checkout_items": checkout_items,
        "items_total_price": items_total_price,
        "shipping_fee": shipping_fee,
        "grand_total": grand_total,
        "cart_count": cart_count,
        "customer": customer,
    }

    return templates.TemplateResponse(
        "/customer/checkout.jinja", context=context, status_code=status.HTTP_200_OK
    )

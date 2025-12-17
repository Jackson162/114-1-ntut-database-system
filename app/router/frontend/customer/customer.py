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

from app.router.schema.sqlalchemy import OrderSchema, OrderItemSchema, BookSchema, BookstoreSchema
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.util.auth import decode_jwt
from app.db.operator.cart import get_cart_item_count, get_cart_details
from app.db.operator.book import (
    search_books, 
    get_all_books, 
    get_all_categories, 
    get_new_arrivals,
    get_book_display_data,
    search_books_with_mappings,
    get_new_arrivals_with_mappings,
    search_books_with_bookstore_details,     
    get_new_arrivals_with_bookstore_details    
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


# 結帳畫面
@router.get("/checkout")
async def checkout_page(request: Request, checkout_error: Optional[str] = None):
    context = {"request": request, "checkout_error": checkout_error}

    return templates.TemplateResponse(
        "/customer/checkout.jinja", context=context, status_code=status.HTTP_200_OK
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
        
        grouped[bs_name].append({
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "image_url": "/static/book.png",
            "min_price": mapping.price,       # 前端 book_card 使用 min_price 變數名
            "bookstore_id": bookstore.bookstore_id,
            "bookstore_name": bookstore.name
        })
    return grouped

@router.get("/home")
async def customer_homepage(
    request: Request,
    q: Optional[str] = None, 
    db: AsyncSession = Depends(get_db_session),
):
    token = request.cookies.get("auth_token")
    customer_account = None
    if token: 
        try:
            payload = decode_jwt(token)
            customer_account = payload.account
        except:
            pass

    cart_count = 0
    if customer_account:
        try:
            cart_count = await get_cart_item_count(db, customer_account)
        except:
            pass
            
    context = {
        "request": request,
        "cart_count": cart_count,
        "q": q or "",
        "grouped_books": {},     # 初始化
        "grouped_new_arrivals": {}, # 初始化
    }

    if q:
        # 搜尋模式：使用新函式並分組
        rows = await search_books_with_bookstore_details(db, q)
        grouped_results = group_results_by_bookstore(rows)
        
        context.update({
            "is_search_mode": True,
            "grouped_books": grouped_results, 
        })
    else:
        # 首頁模式
        categories = []
        try:
            categories = await get_all_categories(db)
        except:
            pass
        
        # 新書：使用新函式並分組
        new_rows = []
        try:
            new_rows = await get_new_arrivals_with_bookstore_details(db)
        except:
            pass
            
        grouped_new_arrivals = group_results_by_bookstore(new_rows)
        
        context.update({
            "is_search_mode": False,
            "categories": categories,
            "grouped_new_arrivals": grouped_new_arrivals, # 傳遞分組後的資料
            # 暫時留空其他區塊
            "bestsellers": [], 
            "promotions": [],  
        })
    
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
        
        cart_items_data.append({
            "cart_item_id": row[0],
            "quantity": quantity,
            "book_id": row[2],
            "title": row[3],
            "author": row[4],
            "image_url": "/static/book.png",
            "bookstore_id": row[6],
            "bookstore_name": row[7], # 確保有這個欄位供模板 groupby 使用
            "price": price,
            "stock": row[9],
            "subtotal": subtotal
        })

    context = {
        "request": request,
        "cart_items": cart_items_data,
        "total_price": total_price,
        "total_items": total_items,
        "cart_count": total_items,
        "customer": customer
    }

    return templates.TemplateResponse(
        "/customer/carts.jinja", context=context, status_code=status.HTTP_200_OK
    )
    
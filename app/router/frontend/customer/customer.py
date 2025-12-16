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
from app.db.operator.cart import get_cart_item_count,get_cart_item
from app.db.operator.book import get_all_categories, get_new_arrivals,get_book_display_data


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

@router.get("/home")
async def customer_homepage(
    request: Request,
    q: Optional[str] = None, # 新增搜尋參數
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
    }

    if q:
        books = await search_books(db, q)
        
        books_data = []
        for b in books:
            books_data.append(await get_book_display_data(db, b))
            
        context.update({
            "is_search_mode": True,
            "books": books_data,
        })
    else:
        categories = []
        try:
            categories = await get_all_categories(db)
        except:
            pass
        
        new_books = []
        try:
            new_books = await get_new_arrivals(db)
        except:
            pass
        
        new_arrivals_data = []
        for b in new_books:
            new_arrivals_data.append(await get_book_display_data(db, b))
        
        context.update({
            "is_search_mode": False,
            "categories": categories,
            "new_arrivals": new_arrivals_data,
            "bestsellers": [], 
            "promotions": [],  
        })
    
    return templates.TemplateResponse(
        "customer/home.jinja", context=context, status_code=status.HTTP_200_OK
    )



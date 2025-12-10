from typing import Tuple, Annotated
from fastapi import APIRouter, Depends, Request, status, Form
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from fastapi.responses import JSONResponse

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.customer import Customer
from app.db.operator.order import get_orders_by_customer_account
from app.util.auth import JwtPayload
from app.router.template.index import templates
from app.db.operator.shopping_cart import (
    get_cart_by_account,
    create_cart,
    get_book_mapping,
    get_cart_item,
    update_cart_item_quantity,
    create_cart_item,
)

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


# shopping-cart api
@router.post("/cart-items")
async def add_to_cart(
    request: Request,
    book_id: Annotated[UUID, Form()],
    bookstore_id: Annotated[UUID, Form()],
    quantity: Annotated[int, Form()] = 1,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    try:
        cart = await get_cart_by_account(db, customer.account)
        if not cart:
            cart = await create_cart(db, customer.account)
        mapping = await get_book_mapping(db, book_id, bookstore_id)
        if not mapping:
            raise Exception("Book/Bookstore mapping not found")

        existing_item = await get_cart_item(db, cart.cart_id, mapping.book_bookstore_mapping_id)

        if existing_item:
            await update_cart_item_quantity(db, existing_item.cart_item_id, quantity)
        else:
            await create_cart_item(db, cart.cart_id, mapping.book_bookstore_mapping_id, quantity)

        await db.commit()

        return {"message": "Successfully added to cart"}

    except Exception as e:
        #  Rollback
        await db.rollback()
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(e)})

from typing import Tuple, Annotated
from fastapi import APIRouter, Depends, Request, status, Form
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

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
    except NoResultFound:
        orders = []
    except Exception as err:
        orders = []
        list_order_error = repr(err)

    orders = [order.dict() for order in orders]

    context = {
        "request": request,
        "customer": customer,
        "orders": orders,
        "list_order_error": list_order_error,
    }

    return templates.TemplateResponse(
        "/customer/orders.jinja", context=context, status_code=status.HTTP_200_OK
    )


# shopping-cart api
@router.post("/cart-items")
async def add_to_cart(
    request: Request,
    # 改用 Form 來接收資料，因為前端是 HTML Form
    book_id: Annotated[UUID, Form()],
    bookstore_id: Annotated[UUID, Form()],  # Reviewer 要求改傳 bookstore_id
    quantity: Annotated[int, Form()] = 1,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    try:
        # 1. 商業邏輯：先找購物車，沒有就建
        cart = await get_cart_by_account(db, customer.account)
        if not cart:
            cart = await create_cart(db, customer.account)
            # 注意：這裡雖然 insert 了，但還沒 commit，所以還在同一個 transaction 內

        # 2. 商業邏輯：確認商品 Mapping 存在 (改用 bookstore_id 查)
        mapping = await get_book_mapping(db, book_id, bookstore_id)
        if not mapping:
            raise Exception("Book/Bookstore mapping not found")

        # 3. 商業邏輯：檢查購物車內是否已有該商品
        existing_item = await get_cart_item(db, cart.cart_id, mapping.book_bookstore_mapping_id)

        if existing_item:
            # 有就更新 (直接覆蓋數量)
            await update_cart_item_quantity(db, existing_item.cart_item_id, quantity)
        else:
            # 沒有就新增
            await create_cart_item(db, cart.cart_id, mapping.book_bookstore_mapping_id, quantity)

        # 4. 全部成功後，一起 Commit
        await db.commit()

        # 這邊看你是要回傳 JSON 還是 Redirect，依照專案慣例
        return {"message": "Successfully added to cart"}

    except Exception as e:
        # 5. 發生錯誤一定要 Rollback
        await db.rollback()
        from fastapi.responses import JSONResponse

        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"error": str(e)})

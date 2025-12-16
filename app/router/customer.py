from typing import Tuple, Annotated
from fastapi import APIRouter, Depends, Request, status, Form
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse, RedirectResponse

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.customer import Customer
from app.db.operator.order import create_order, create_order_item
from app.db.operator.inventory import decrease_stock
from app.util.auth import JwtPayload
from app.router.template.index import templates
from app.db.operator.bookbookstoremapping import get_book_mapping
from app.db.operator.shopping_cart import (
    get_cart_by_account,
    create_cart,
    get_cart_item,
    update_cart_item_quantity,
    create_cart_item,
    clear_cart_items,
)


router = APIRouter()

validate_customer_token = validate_token_by_role(UserRole.CUSTOMER)


# shopping-cart api
@router.post("/cart-items/create")
async def add_to_cart(
    request: Request,
    book_id: Annotated[UUID, Form()],
    bookstore_id: Annotated[UUID, Form()],
    quantity: Annotated[int, Form()],
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


# dealing with order
@router.post("/orders/create")
async def create_customer_order(
    request: Request,
    recipient_name: Annotated[str, Form()],
    recipient_phone: Annotated[str, Form()],
    recipient_address: Annotated[str, Form()],
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    try:
        cart = await get_cart_by_account(db, customer.account)
        if not cart or not cart.cart_items:
            raise Exception("Cart is empty")

        total_price = 0
        shipping_fee = 60  # 先假設60，到時候再想辦法= =

        order_items_data = []  # 暫存要寫入的資料

        # 3.1 遍歷購物車，檢查庫存並計算總價
        # 注意：你需要確保 cart.cart_items 有被載入 (Eager Loading)

        for item in cart.cart_items:
            mapping = await get_book_mapping(
                db, item.book_bookstore_mapping.book_id, item.book_bookstore_mapping.bookstore_id
            )

            if not mapping:
                raise Exception(f"Product not found for item {item.cart_item_id}")

            # 檢查庫存 (雖然 Operator 不檢查，但 Router 可以檢查以提供更好的錯誤訊息)
            if mapping.store_quantity < item.quantity:
                raise Exception(f"Insufficient stock for book: {mapping.book.title}")

            item_total = mapping.price * item.quantity
            total_price += item_total

            # 暫存資料，等等寫入
            order_items_data.append(
                {
                    "mapping_id": mapping.book_bookstore_mapping_id,
                    "price": mapping.price,
                    "quantity": item.quantity,
                }
            )

        # 4. 寫入訂單 (Create Order)
        new_order = await create_order(
            db=db,
            account=customer.account,
            customer_name=customer.name,
            customer_phone=customer.phone_number,
            customer_email=customer.email,
            address=recipient_address,
            total_price=total_price + shipping_fee,
            shipping_fee=shipping_fee,
            recipient_name=recipient_name,
        )

        # 5. 寫入細項 (Order Items) & 扣庫存
        for data in order_items_data:
            # 5.1 建立細項
            await create_order_item(
                db=db,
                order_id=new_order.order_id,
                mapping_id=data["mapping_id"],
                quantity=data["quantity"],
                price=data["price"],
            )
            # 5.2 扣庫存
            await decrease_stock(db=db, mapping_id=data["mapping_id"], quantity=data["quantity"])

        await clear_cart_items(db, cart.cart_id)

        await db.commit()

        # 8. 跳轉到訂單列表或成功頁面
        return RedirectResponse(
            url="/frontend/customers/orders/success", status_code=status.HTTP_303_SEE_OTHER
        )

    except Exception as e:
        await db.rollback()
        # 回傳錯誤 (或是跳轉回購物車頁面帶 Error Message)
        return templates.TemplateResponse(
            "/customer/checkout.jinja",
            context={
                "request": request,
                "error": str(e),
                "recipient_name": recipient_name,
                "recipient_phone": recipient_phone,
                "recipient_address": recipient_address,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )

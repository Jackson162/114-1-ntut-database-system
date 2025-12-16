from typing import Tuple, Annotated, Dict, List
from datetime import datetime

from fastapi import APIRouter, Depends, Request, status, Form
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse, RedirectResponse

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.customer import Customer
from app.db.models.cart_item import CartItem
from app.db.models.order import Order

from app.util.auth import JwtPayload
from app.db.operator.order import create_order, create_order_item
from app.db.operator.bookbookstoremapping import get_book_mapping, decrease_stock
from app.db.operator.shopping_cart import (
    get_cart_by_account,
    create_cart,
    get_cart_item,
    update_cart_item_quantity,
    create_cart_item,
    clear_cart_items,
)
from app.db.operator.coupon import get_coupon_by_id
from app.enum.order import OrderStatus
from app.util.coupon import apply_coupon
from app.logging.logger import get_logger

logger = get_logger()

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
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"error": str(e)}
        )


# dealing with order
@router.post("/orders/create")
async def create_customer_order(
    request: Request,
    recipient_name: Annotated[str, Form()],
    coupon_id: Annotated[UUID, Form()],
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    try:
        cart = await get_cart_by_account(db, customer.account)
        if not cart or not cart.cart_items:
            raise Exception("Cart is empty")

        coupon = await get_coupon_by_id(db=db, coupon_id=coupon_id)

        if not coupon:
            raise Exception(f"Coupon with id: {coupon_id} does not exist!")

        cur_time = datetime.now().date()
        if cur_time < coupon.start_date:
            err_msg = f"Coupon: name: {coupon.name}, id: {coupon.coupon_id} is inactive."
            logger.error(err_msg)
            raise Exception(err_msg)

        if coupon.end_date and cur_time >= coupon.end_date:
            err_msg = f"Coupon: name: {coupon.name}, id: {coupon.coupon_id} is expired."
            logger.error(err_msg)
            raise Exception(err_msg)

        coupon_bookstore_id = coupon.staff.bookstore_id if coupon.staff else None

        bookstore_id_to_cart_items: Dict[UUID, List[CartItem]] = {}

        for cart_item in cart.cart_items:
            bookstore_id = cart_item.book_bookstore_mapping.bookstore_id
            if bookstore_id not in bookstore_id_to_cart_items:
                bookstore_id_to_cart_items[bookstore_id] = []
            bookstore_id_to_cart_items[bookstore_id].append(cart_item)

        for bookstore_id, cart_items in bookstore_id_to_cart_items.items():
            bookstore = cart_items[0].book_bookstore_mapping.bookstore

            order_items_data = []

            # 3.1 遍歷購物車，檢查庫存並計算總價
            # 注意：你需要確保 cart.cart_items 有被載入 (Eager Loading)
            item_total_price = 0

            for item in cart_items:
                mapping = await get_book_mapping(
                    db,
                    item.book_bookstore_mapping.book_id,
                    item.book_bookstore_mapping.bookstore_id,
                )

                if not mapping:
                    raise Exception(f"Product not found for item {item.cart_item_id}")

                # 檢查庫存 (雖然 Operator 不檢查，但 Router 可以檢查以提供更好的錯誤訊息)
                if mapping.store_quantity < item.quantity:
                    raise Exception(f"Insufficient stock for book: {mapping.book.title}")

                item_total_price = mapping.price * item.quantity
                item_total_price += item_total_price

                # 暫存資料，等等寫入
                order_items_data.append(
                    {
                        "mapping_id": mapping.book_bookstore_mapping_id,
                        "price": mapping.price,
                        "quantity": item.quantity,
                    }
                )

            order = Order(
                customer_account=customer.account,
                order_time=datetime.now().date(),
                customer_name=customer.name,
                customer_phone_number=customer.phone,
                customer_email=customer.email,
                shipping_address=bookstore.shipping_fee,
                total_price=item_total_price + bookstore.shipping_fee,
                shipping_fee=bookstore.shipping_fee,
                recipient_name=recipient_name,
                status=OrderStatus.DELIVERING,
            )

            try:
                order = apply_coupon(
                    coupon=coupon,
                    order=order,
                    coupon_bookstore_id=coupon_bookstore_id,
                    order_bookstore_id=bookstore.bookstore_id,
                )
            except Exception:
                pass

            # 4. 寫入訂單 (Create Order)
            order = await create_order(db=db, order=order)

            # 5. 寫入細項 (Order Items) & 扣庫存
            for data in order_items_data:
                # 5.1 建立細項
                await create_order_item(
                    db=db,
                    order_id=order.order_id,
                    mapping_id=data["mapping_id"],
                    quantity=data["quantity"],
                    price=data["price"],
                )
                # 5.2 扣庫存
                await decrease_stock(
                    db=db, mapping_id=data["mapping_id"], quantity=data["quantity"]
                )

        await clear_cart_items(db, cart.cart_id)

        await db.commit()

        # 8. 跳轉到訂單列表或成功頁面
        return RedirectResponse(
            url="/frontend/customers/orders?checkout_succeeds=true",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except Exception as err:
        await db.rollback()
        return RedirectResponse(
            url=f"/frontend/customers/checkout?checkout_error={repr(err)}",
            status_code=status.HTTP_303_SEE_OTHER,
        )

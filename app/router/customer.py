from typing import Tuple, Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Request, status, Form
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse, RedirectResponse

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.customer import Customer
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
    delete_cart_item_by_item_ids,
    get_cart_item_by_item_id,
)
from app.db.operator.coupon import get_coupon_by_id
from app.enum.order import OrderStatus
from app.util.coupon import apply_coupon
from app.logging.logger import get_logger

logger = get_logger()

router = APIRouter()

validate_customer_token = validate_token_by_role(UserRole.CUSTOMER)


# shopping-cart api
@router.post("/cart-items/create_or_update")
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

        if existing_item and quantity > 0:
            await update_cart_item_quantity(db, existing_item.cart_item_id, quantity)
        elif existing_item and quantity <= 0:
            await delete_cart_item_by_item_ids(db=db, cart_item_ids=[existing_item.cart_item_id])
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


@router.post("/cart-items/{cart_item_id}/delete")
async def remove_from_cart(
    request: Request,
    cart_item_id: UUID,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    try:
        cart = await get_cart_by_account(db, customer.account)

        if not cart:
            raise Exception("The Cart of this customer is not found")
        existing_item = await get_cart_item_by_item_id(db=db, cart_item_id=cart_item_id)

        if existing_item:
            await delete_cart_item_by_item_ids(db=db, cart_item_ids=[existing_item.cart_item_id])

        await db.commit()
        return RedirectResponse(
            url="/frontend/customers/carts",
            status_code=status.HTTP_303_SEE_OTHER,
        )
    except Exception as err:
        await db.rollback()
        return RedirectResponse(
            url=f"/frontend/customers/carts?remove_from_cart_error={repr(err)}",
            status_code=status.HTTP_303_SEE_OTHER,
        )


# dealing with order
@router.post("/orders/create")
async def create_customer_order(
    request: Request,
    recipient_name: Annotated[str, Form()],
    recipient_address: Annotated[str, Form()],
    bookstore_id: Annotated[UUID, Form()],
    coupon_id: Annotated[Optional[UUID], Form()] = None,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_customer_token),
    db: AsyncSession = Depends(get_db_session),
):
    token_payload, customer = login_data

    try:
        cart = await get_cart_by_account(db, customer.account)
        if not cart or not cart.cart_items:
            raise Exception("Cart is empty")

        coupon = None

        if coupon_id:
            coupon = await get_coupon_by_id(db=db, coupon_id=coupon_id)

        coupon_bookstore_id = None

        if coupon:
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

        target_cart_items = []

        for cart_item in cart.cart_items:
            item_bookstore_id = cart_item.book_bookstore_mapping.bookstore_id

            if item_bookstore_id == bookstore_id:
                target_cart_items.append(cart_item)

        if not target_cart_items:
            raise Exception("No cart items from the bookstore exist!")

        bookstore = target_cart_items[0].book_bookstore_mapping.bookstore

        order_items_data = []

        # 3.1 遍歷購物車，檢查庫存並計算總價
        # 注意：你需要確保 cart.cart_items 有被載入 (Eager Loading)
        item_total_price = 0

        for item in target_cart_items:
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

            sub_total_price = mapping.price * item.quantity
            item_total_price += sub_total_price

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
            customer_phone_number=customer.phone_number,
            customer_email=customer.email,
            shipping_address=recipient_address,
            total_price=item_total_price + bookstore.shipping_fee,
            shipping_fee=bookstore.shipping_fee,
            recipient_name=recipient_name,
            status=OrderStatus.DELIVERING.value,
        )

        if coupon:
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
            await decrease_stock(db=db, mapping_id=data["mapping_id"], quantity=data["quantity"])

        await delete_cart_item_by_item_ids(
            db=db, cart_item_ids=[item.cart_item_id for item in target_cart_items]
        )

        await db.commit()

        # 8. 跳轉到訂單列表或成功頁面
        return RedirectResponse(
            url="/frontend/customers/orders?checkout_succeeds=true",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    except Exception as err:
        logger.error(err)
        await db.rollback()
        return RedirectResponse(
            url=(
                f"/frontend/customers/checkout"
                f"?bookstore_id={bookstore_id}&checkout_error={repr(err)}"
            ),
            status_code=status.HTTP_303_SEE_OTHER,
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

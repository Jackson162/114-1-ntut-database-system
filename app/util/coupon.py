from typing import Optional
from uuid import UUID
from datetime import datetime
from app.db.models.order import Order
from app.db.models.coupon import Coupon
from app.enum.coupon import CouponType
from app.logging.logger import get_logger

logger = get_logger()


def apply_coupon(
    coupon: Coupon,
    order: Order,
    coupon_bookstore_id: Optional[UUID] = None,
    order_bookstore_id: Optional[UUID] = None,
):
    if coupon.staff_account:
        if not coupon_bookstore_id or not order_bookstore_id:
            raise Exception(
                "For bookstore-specific coupon, please provide"
                " both coupon_bookstore_id and order_bookstore_id"
            )
        if str(coupon_bookstore_id) != str(order_bookstore_id):
            raise Exception(
                f"Coupon from bookstore(id={coupon_bookstore_id}) cannot be applied to"
                f" the order of bookstore(id={order_bookstore_id})"
            )

    cur_time = datetime.now().date()
    if cur_time < coupon.start_date:
        raise Exception(f"Coupon: name: {coupon.name}, id: {coupon.coupon_id} is inactive.")

    if coupon.end_date and cur_time > coupon.end_date:
        raise Exception(f"Coupon: name: {coupon.name}, id: {coupon.coupon_id} is expired.")

    items_total_price = order.total_price - order.shipping_fee

    if coupon.type == CouponType.SHIPPING.value:
        order.shipping_fee = round(order.shipping_fee * (1 - coupon.discount_percentage))
        order.total_price = items_total_price + order.shipping_fee
    if coupon.type == CouponType.SEASONINGS.value:
        order.total_price = round(order.total_price * (1 - coupon.discount_percentage))
    elif coupon.type == CouponType.SPECIAL_EVENT.value:
        order.total_price = (
            round(items_total_price * (1 - coupon.discount_percentage)) + order.shipping_fee
        )

    return order

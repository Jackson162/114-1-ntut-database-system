from datetime import datetime
from app.db.models.order import Order
from app.db.models.coupon import Coupon
from app.enum.coupon import CouponType


def apply_coupon(coupon: Coupon, order: Order):
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

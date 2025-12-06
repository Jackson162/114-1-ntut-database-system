"""
Class definition for Order
"""

from datetime import date
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Integer, Text, text, CHAR, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.customer import Customer
    from app.db.models.order_item import OrderItem
    from app.db.models.coupon import Coupon


class Order(Base):
    """
    ORM class for order_
    """

    __tablename__ = "order_"

    order_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    order_time: Mapped[date] = mapped_column(Date, nullable=False)
    customer_name: Mapped[str] = mapped_column(Text, nullable=False)
    customer_phone_number: Mapped[str] = mapped_column(CHAR(10), nullable=False)
    customer_email: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    total_price: Mapped[int] = mapped_column(Integer, nullable=False)
    shipping_address: Mapped[str] = mapped_column(Text, nullable=False)
    shipping_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    recipient_name: Mapped[str] = mapped_column(Text, nullable=False)

    coupon_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("coupon.coupon_id"))
    customer_account: Mapped[str] = mapped_column(ForeignKey("customer.account"), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
    coupon: Mapped["Coupon"] = relationship(back_populates="orders")

    __table_args__ = (
        CheckConstraint(total_price >= 0, name="total_price_non_negative"),
        CheckConstraint(shipping_fee >= 0, name="shipping_fee_non_negative"),
    )

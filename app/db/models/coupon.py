"""
Class definition for Coupon
"""

from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING, List

from uuid import UUID

from sqlalchemy import Date, ForeignKey, Numeric, Text, text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.admin import Admin
    from app.db.models.staff import Staff
    from app.db.models.order import Order


class Coupon(Base):
    """
    ORM class for coupon
    """

    __tablename__ = "coupon"

    coupon_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    type: Mapped[str] = mapped_column(Text, nullable=False)
    discount_percentage: Mapped[Decimal] = mapped_column(Numeric, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    admin_account: Mapped[Optional[str]] = mapped_column(ForeignKey("admin.account"))
    staff_account: Mapped[Optional[str]] = mapped_column(ForeignKey("staff.account"))

    admin: Mapped[Optional["Admin"]] = relationship(back_populates="coupons")
    staff: Mapped[Optional["Staff"]] = relationship(back_populates="coupons")
    orders: Mapped[List["Order"]] = relationship(back_populates="coupon")

    __table_args__ = (
        CheckConstraint(
            (discount_percentage >= 0) & (discount_percentage <= 1),
            name="discount_percentage_check",
        ),
    )

"""
Class definition for Staff
"""

from typing import TYPE_CHECKING, Optional, List
from uuid import UUID

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.bookstore import Bookstore
    from app.db.models.coupon import Coupon


class Staff(Base):
    """
    ORM class for staff
    """

    __tablename__ = "staff"

    account: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    bookstore_id: Mapped[UUID] = mapped_column(ForeignKey("bookstore.bookstore_id"), nullable=True)

    bookstore: Mapped["Bookstore"] = relationship(back_populates="staffs")
    coupons: Mapped[Optional[List["Coupon"]]] = relationship(back_populates="staff")

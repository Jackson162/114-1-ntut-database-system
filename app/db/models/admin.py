"""
Class definition for Admin
"""

from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import Text
from app.db.models.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from app.db.models.coupon import Coupon


class Admin(Base):
    """
    ORM class for admin
    """

    __tablename__ = "admin"

    account: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)

    coupons: Mapped[Optional[List["Coupon"]]] = relationship(back_populates="admin")

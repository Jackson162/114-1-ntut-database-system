"""
Class definition for Customer
"""

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Text, CHAR
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base

if TYPE_CHECKING:
    from app.db.models.order import Order


class Customer(Base):
    """
    ORM class for customer
    """

    __tablename__ = "customer"

    account: Mapped[str] = mapped_column(Text, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    password: Mapped[str] = mapped_column(Text, nullable=False)
    email: Mapped[Optional[str]] = mapped_column(Text)
    phone_number: Mapped[str] = mapped_column(CHAR(10), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text)

    orders: Mapped[List["Order"]] = relationship(back_populates="customer")

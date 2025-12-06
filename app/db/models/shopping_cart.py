"""
Class definition for ShoppingCart
"""

from typing import TYPE_CHECKING, List
from uuid import UUID

from sqlalchemy import ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.cart_item import CartItem


class ShoppingCart(Base):
    """
    ORM class for shopping_cart
    """

    __tablename__ = "shopping_cart"

    cart_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    customer_account: Mapped[str] = mapped_column(ForeignKey("customer.account"))

    cart_items: Mapped[List["CartItem"]] = relationship(back_populates="cart")

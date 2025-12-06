"""
Class definition for CartItem
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.shopping_cart import ShoppingCart
    from app.db.models.book_bookstore_mapping import BookBookstoreMapping


class CartItem(Base):
    """
    ORM class for cart_item
    """

    __tablename__ = "cart_item"

    cart_item_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    cart_id: Mapped[UUID] = mapped_column(ForeignKey("shopping_cart.cart_id"), nullable=False)
    book_bookstore_mapping_id: Mapped[UUID] = mapped_column(
        ForeignKey("book_bookstore_mapping.book_bookstore_mapping_id")
    )

    cart: Mapped["ShoppingCart"] = relationship(back_populates="cart_items")
    book_bookstore_mapping: Mapped["BookBookstoreMapping"] = relationship(
        back_populates="cart_items"
    )
    __table_args__ = (CheckConstraint(quantity >= 0, name="quantity_non_negative"),)

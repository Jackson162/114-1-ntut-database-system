"""
Class definition for OrderItem
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.order import Order
    from app.db.models.book_bookstore_mapping import BookBookstoreMapping


class OrderItem(Base):
    """
    ORM class for order_item
    """

    __tablename__ = "order_item"

    order_item_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[int] = mapped_column(Integer)

    order_id: Mapped[UUID] = mapped_column(ForeignKey("order_.order_id"))
    book_bookstore_mapping_id: Mapped[UUID] = mapped_column(
        ForeignKey("book_bookstore_mapping.book_bookstore_mapping_id")
    )

    order: Mapped["Order"] = relationship(back_populates="order_items")
    book_bookstore_mapping: Mapped["BookBookstoreMapping"] = relationship(
        back_populates="order_items"
    )

    __table_args__ = (
        CheckConstraint(quantity >= 0, name="quantity_non_negative"),
        CheckConstraint(price >= 0, name="price_non_negative"),
    )

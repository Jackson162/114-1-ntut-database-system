"""
Class definition for BookBookstoreMapping
"""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.book import Book
    from app.db.models.bookstore import Bookstore
    from app.db.models.order_item import OrderItem
    from app.db.models.cart_item import CartItem


class BookBookstoreMapping(Base):
    """
    ORM class for book_bookstore_mapping
    """

    __tablename__ = "book_bookstore_mapping"

    book_bookstore_mapping_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    store_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    book_id: Mapped[UUID] = mapped_column(ForeignKey("book.book_id"))
    bookstore_id: Mapped[UUID] = mapped_column(ForeignKey("bookstore.bookstore_id"))

    book: Mapped["Book"] = relationship(back_populates="book_bookstore_mapping")
    bookstore: Mapped["Bookstore"] = relationship(back_populates="book_bookstore_mapping")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="book_bookstore_mapping")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="book_bookstore_mapping")

    __table_args__ = (
        CheckConstraint(price >= 0, name="price_non_negative"),
        CheckConstraint(store_quantity >= 0, name="store_quantity_non_negative"),
    )

"""
Class definition for BookBookstoreMapping
"""

from uuid import UUID

from sqlalchemy import ForeignKey, Integer, text, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


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

    __table_args__ = (
        CheckConstraint(price >= 0, name="price_non_negative"),
        CheckConstraint(store_quantity >= 0, name="store_quantity_non_negative"),
    )

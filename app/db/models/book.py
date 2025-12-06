"""
Class definition for Book
"""

from datetime import date
from typing import Optional, TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, Text, text, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.book_bookstore_mapping import BookBookstoreMapping


class Book(Base):
    """
    ORM class for book
    """

    __tablename__ = "book"

    book_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    author: Mapped[str] = mapped_column(Text, nullable=False)
    publisher: Mapped[str] = mapped_column(Text, nullable=False)
    isbn: Mapped[str] = mapped_column(String(17), nullable=False, unique=True)
    category: Mapped[Optional[str]] = mapped_column(Text)
    series: Mapped[Optional[str]] = mapped_column(Text)
    publish_date: Mapped[Optional[date]] = mapped_column(Date)

    book_bookstore_mapping: Mapped["BookBookstoreMapping"] = relationship(back_populates="book")

"""
Class definition for Bookstore
"""

from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from sqlalchemy import Integer, Text, text, CHAR, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base

if TYPE_CHECKING:
    from app.db.models.staff import Staff
    from app.db.models.book_bookstore_mapping import BookBookstoreMapping


class Bookstore(Base):
    """
    ORM class for bookstore
    """

    __tablename__ = "bookstore"

    bookstore_id: Mapped[UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    phone_number: Mapped[str] = mapped_column(CHAR(10), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(Text)
    shipping_fee: Mapped[int] = mapped_column(Integer, nullable=False)

    # Relationships
    staffs: Mapped[List["Staff"]] = relationship(back_populates="bookstore")
    book_bookstore_mapping: Mapped["BookBookstoreMapping"] = relationship(
        back_populates="book_store"
    )

    __table_args__ = (CheckConstraint(shipping_fee >= 0, name="shipping_fee_non_negative"),)

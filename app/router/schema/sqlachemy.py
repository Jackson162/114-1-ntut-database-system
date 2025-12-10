from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date
from decimal import Decimal


class BookSchema(BaseModel):
    book_id: UUID
    title: str
    author: str
    publisher: str
    isbn: str
    category: str
    series: Optional[str] = None
    publish_date: date

    class Config:
        orm_mode = True


class BookBookstoreMappingSchema(BaseModel):
    book_bookstore_mapping_id: UUID
    price: int
    store_quantity: int
    book_id: UUID
    bookstore_id: UUID

    class Config:
        orm_mode = True


class BookstoreSchema(BaseModel):
    bookstore_id: UUID
    name: str
    phone_number: str
    email: Optional[str] = None
    address: Optional[str] = None
    shipping_fee: int

    class Config:
        orm_mode = True


class CouponSchema(BaseModel):
    coupon_id: UUID
    type: str
    discount_percentage: Decimal
    start_date: date
    end_date: Optional[date] = None
    admin_account: Optional[str] = None
    staff_account: Optional[str] = None

    class Config:
        orm_mode = True


class CustomerSchema(BaseModel):
    account: str
    name: str
    email: Optional[str] = None
    phone_number: str
    address: Optional[str] = None

    class Config:
        orm_mode = True


class OrderItemSchema(BaseModel):
    order_item_id: UUID
    quantity: int
    price: Optional[int]
    order_id: UUID
    book_bookstore_mapping_id: UUID

    class Config:
        orm_mode = True


class OrderSchema(BaseModel):
    order_id: UUID
    order_time: date
    customer_name: str
    customer_phone_number: str
    customer_email: Optional[str] = None
    status: str
    total_price: int
    shipping_address: str
    shipping_fee: int
    recipient_name: str
    coupon_id: Optional[UUID] = None
    customer_account: str

    class Config:
        orm_mode = True

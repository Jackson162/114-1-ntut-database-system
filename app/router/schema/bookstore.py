from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class BookstoreSchema(BaseModel):
    bookstore_id: UUID
    name: str
    phone_number: str
    email: Optional[str]
    address: Optional[str]
    shipping_fee: int
    verified: bool

    class Config:
        orm_mode = True

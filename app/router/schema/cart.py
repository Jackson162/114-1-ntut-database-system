from pydantic import BaseModel
from uuid import UUID


class CartItemCreateRequest(BaseModel):
    book_id: UUID
    price: int
    quantity: int = 1  # 預設加入 1 本

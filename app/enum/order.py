from enum import StrEnum


class OrderStatus(StrEnum):
    RECEIVED = "received"
    PROCESSING = "processing"
    SHIPPING = "shipping"
    CLOSED = "closed"

from enum import StrEnum


class OrderStatus(StrEnum):
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    COMPLETED = "completed"

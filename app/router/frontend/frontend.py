from fastapi import APIRouter
from app.router.frontend.auth import auth
from app.router.frontend.customer import customer

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(customer.router, prefix="/customers", tags=["customers"])

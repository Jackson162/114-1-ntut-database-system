from fastapi import APIRouter
from app.router.frontend.auth import auth
from app.router.frontend.customer import customer
from app.router.frontend.staff import staff

router = APIRouter()

router.include_router(auth.router, prefix="/auth")
router.include_router(customer.router, prefix="/customers")
router.include_router(staff.router, prefix="/staffs")

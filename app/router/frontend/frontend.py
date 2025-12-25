from fastapi import APIRouter
from app.router.frontend.auth import auth
from app.router.frontend.customer import customer
from app.router.frontend.staff import staff
from app.router.frontend.admin import admin

router = APIRouter()

router.include_router(auth.router, prefix="/auth")
router.include_router(customer.router, prefix="/customers")
router.include_router(staff.router, prefix="/staffs")
router.include_router(admin.router, prefix="/admin")

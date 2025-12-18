from typing import Tuple
from fastapi import APIRouter, Depends, Request, status, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.router.template.index import templates
from app.middleware.db_session import get_db_session
from app.middleware.depends import validate_token_by_role
from app.enum.user import UserRole
from app.util.auth import JwtPayload
from app.db.models.admin import Admin
from app.db.operator.customer import get_all_customers#, update_customer_status, update_customer_info
from app.db.operator.staff import get_all_staffs

router = APIRouter()

# Dependency: 驗證是否為管理員
AdminDep = Tuple[JwtPayload, Admin]

@router.get("/home", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user_data: AdminDep = Depends(validate_token_by_role(UserRole.ADMIN))
):
    """管理員首頁 (Dashboard)"""
    _, admin = user_data
    return templates.TemplateResponse(
        "admin/home.jinja",
        {"request": request, "admin": admin, "active_page": "dashboard"}
    )

@router.get("/users", response_class=HTMLResponse)
async def user_management(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    user_data: AdminDep = Depends(validate_token_by_role(UserRole.ADMIN))
):
    """使用者與員工帳號管理頁面"""
    _, admin = user_data
    customers = await get_all_customers(db)
    staffs = await get_all_staffs(db) 
    return templates.TemplateResponse(
        "admin/users.jinja",
        {
            "request": request,
            "admin": admin,
            "customers": customers,
            "staffs": staffs, 
            "active_page": "users"
        }
    )

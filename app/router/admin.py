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
from app.db.operator.customer import get_all_customers, update_customer_info

router = APIRouter()

AdminDep = Tuple[JwtPayload, Admin]

#@router.patch("/users/{account}/status")
#async def toggle_user_status(
#    account: str,
#    request: Request,
#    db: AsyncSession = Depends(get_db_session),
#    user_data: AdminDep = Depends(validate_token_by_role(UserRole.ADMIN))
#):
#    """啟用/停用 使用者帳號"""
#    try:
#        data = await request.json()
#        is_active = data.get("is_active")
#        if is_active is None:
#            raise HTTPException(status_code=400, detail="Missing is_active field")
#        
#        await update_customer_status(db, account, is_active)
#        return {"message": "Status updated"}
#    except Exception as e:
#        raise HTTPException(status_code=500, detail=str(e))

@router.put("/users/{account}")
async def edit_user_info(
    account: str,
    request: Request,
    db: AsyncSession = Depends(get_db_session),
    user_data: AdminDep = Depends(validate_token_by_role(UserRole.ADMIN))
):
    """編輯使用者資料"""
    try:
        data = await request.json()
        name = data.get("name")
        email = data.get("email")
        
        await update_customer_info(db, account, name, email)
        return {"message": "User info updated"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
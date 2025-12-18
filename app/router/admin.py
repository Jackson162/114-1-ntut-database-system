from typing import Tuple, Annotated, Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, Request, status, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.router.template.index import templates
from app.middleware.db_session import get_db_session
from app.middleware.depends import validate_token_by_role
from app.enum.user import UserRole
from app.enum.coupon import CouponType
from app.util.auth import JwtPayload
from app.db.models.admin import Admin
from app.db.operator.customer import get_all_customers, update_customer_info, delete_customer
from app.db.operator.staff import delete_staff
from app.db.operator.coupon import create_coupon, delete_coupon

router = APIRouter()

AdminDep = Tuple[JwtPayload, Admin]

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

@router.delete("/users/{account}")
@router.delete("/users/{account}")
async def remove_customer(
    account: str,
    db: AsyncSession = Depends(get_db_session),
    user_data: AdminDep = Depends(validate_token_by_role(UserRole.ADMIN))
):
    """刪除 Customer"""
    try:
        await delete_customer(db, account)
        return {"message": "Customer deleted"}
    except InterruptedError:  
        raise HTTPException(status_code=400, detail="無法刪除該使用者，因為仍有相關聯的資料 (如訂單、購物車等)")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/staffs/{account}")
async def remove_staff(
    account: str,
    db: AsyncSession = Depends(get_db_session),
    user_data: AdminDep = Depends(validate_token_by_role(UserRole.ADMIN))
):
    """刪除 Staff"""
    try:
        await delete_staff(db, account)
        return {"message": "Staff deleted"}
    except InterruptedError: 
        raise HTTPException(status_code=400, detail="無法刪除該員工，因為仍有相關聯的資料")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@router.post("/coupons", response_class=RedirectResponse)
async def create_admin_coupon(
    request: Request,
    name: Annotated[str, Form()],
    type: Annotated[CouponType, Form()],
    discount_percentage: Annotated[float, Form()],
    start_date: Annotated[date, Form()],
    end_date: Annotated[Optional[date], Form()] = None,
    db: AsyncSession = Depends(get_db_session),
    user_data: AdminDep = Depends(validate_token_by_role(UserRole.ADMIN))
):
    """Admin 建立平台優惠券"""
    _, admin = user_data
    try:
        await create_coupon(
            db=db,
            account=admin.account,
            name=name,
            type=type,
            discount_percentage=discount_percentage,
            start_date=start_date,
            end_date=end_date,
            role=UserRole.ADMIN,
        )
        await db.commit()
        return RedirectResponse("/frontend/admin/coupons", status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create coupon: {str(e)}")

 
@router.delete("/coupons/{coupon_id}")
async def remove_coupon(
    coupon_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    user_data: AdminDep = Depends(validate_token_by_role(UserRole.ADMIN))
):
    """Admin 刪除任意優惠券"""
    try:
        result = await delete_coupon(db, coupon_id)
        if not result:
             raise HTTPException(status_code=404, detail="Coupon not found")
        await db.commit()
        return {"message": "Coupon deleted"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


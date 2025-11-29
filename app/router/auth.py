from typing import Optional, Annotated
from fastapi import APIRouter, Depends, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.operator.customer import create_customer, get_customer_by_account
from app.db.operator.staff import create_staff, get_staff_by_account
from app.db.operator.admin import get_admin_by_account
from app.util.auth import hash_password, validate_password, generate_jwt
from app.router.schema.auth import LoginData

router = APIRouter()


@router.post("/register", response_class=RedirectResponse)
async def register(
    role: Annotated[str, Form()],
    name: Annotated[str, Form()],
    password: Annotated[str, Form()],
    account: Annotated[str, Form()],
    phone_number: Annotated[Optional[str], Form()] = None,
    email: Annotated[Optional[str], Form()] = None,
    address: Annotated[Optional[str], Form()] = None,
    db: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    try:
        hashed_password = hash_password(password)
        if role == UserRole.CUSTOMER.value and phone_number:
            await create_customer(
                name=name,
                password=hashed_password,
                account=account,
                phone_number=phone_number,
                email=email,
                address=address,
                db=db,
            )
        elif role == UserRole.STAFF.value:
            await create_staff(name=name, password=hashed_password, account=account, db=db)

        await db.commit()
    except Exception as err:
        await db.rollback()
        redirect_url = f"/frontend/auth/register?register_error={repr(err)}"
        return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)

    redirect_url = "/frontend/auth/login?register_succeeded=true"
    return RedirectResponse(redirect_url, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/login", response_class=HTMLResponse)
async def login(
    login_data: LoginData,
    db: AsyncSession = Depends(get_db_session),
):
    try:
        role = login_data.role
        account = login_data.account
        password = login_data.password
        try:
            if role == UserRole.CUSTOMER.value:
                user = await get_customer_by_account(db=db, account=account)
                next_page_path = "/frontend/auth/user_login_succeeded"
            elif role == UserRole.STAFF.value:
                user = await get_staff_by_account(db=db, account=account)
                next_page_path = "/frontend/auth/staff_login_succeeded"
            elif role == UserRole.ADMIN.value:
                user = await get_admin_by_account(db=db, account=account)
                next_page_path = "/frontend/auth/admin_login_succeeded"
            else:
                raise Exception(f"Invalid role: {role}")
        except NoResultFound:
            raise Exception(f"The {role} with this account: {account} does not exist")

        hashed_password = user.password

        if validate_password(password=password, hashed_password=hashed_password):
            expires_in_seconds: int = 86400 * 30
            auth_token = generate_jwt(
                account=account, role=role, expires_in_seconds=expires_in_seconds
            )
            response = JSONResponse(
                content={"next_page_path": next_page_path, "auth_token": auth_token},
                status_code=200,
            )
            response.set_cookie(
                key="auth_token",
                value=auth_token,
                max_age=expires_in_seconds,
                httponly=True,
                secure=True,
                samesite="lax",
                path="/",
            )
            return response
        else:
            raise Exception("This password is wrong")

    except Exception as err:
        return JSONResponse(
            content={"error": repr(err)},
            status_code=500,
        )

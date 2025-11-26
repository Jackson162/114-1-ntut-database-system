from typing import Optional
from fastapi import APIRouter, status, Request
from fastapi.responses import HTMLResponse

from app.router.template.index import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
    register_succeeded: bool = False,
) -> HTMLResponse:
    context = {
        "request": request,
        "register_succeeded": register_succeeded,
    }
    return templates.TemplateResponse(
        "/auth/login.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
    register_error: Optional[str] = None,
) -> HTMLResponse:
    context = {
        "request": request,
        "register_error": register_error,
    }
    return templates.TemplateResponse(
        "/auth/register.jinja", context=context, status_code=status.HTTP_200_OK
    )


# testing
@router.get("/user_login_succeeded", response_class=HTMLResponse)
async def user_login_succeeded_page(
    request: Request,
) -> HTMLResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse(
        "/test/user_login.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/staff_login_succeeded", response_class=HTMLResponse)
async def staff_login_succeeded_page(
    request: Request,
) -> HTMLResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse(
        "/test/staff_login.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/admin_login_succeeded", response_class=HTMLResponse)
async def admin_login_succeeded_page(
    request: Request,
) -> HTMLResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse(
        "/test/admin_login.jinja", context=context, status_code=status.HTTP_200_OK
    )

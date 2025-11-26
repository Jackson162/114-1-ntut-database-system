from fastapi import APIRouter, status, Request
from fastapi.responses import HTMLResponse

from app.router.template.index import templates

router = APIRouter()


@router.get("/login", response_class=HTMLResponse)
async def login_page(
    request: Request,
) -> HTMLResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse(
        "login.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/register", response_class=HTMLResponse)
async def register_page(
    request: Request,
) -> HTMLResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse(
        "register.jinja", context=context, status_code=status.HTTP_200_OK
    )

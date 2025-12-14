from typing import Optional, Tuple
from uuid import UUID
from fastapi import APIRouter, Depends, Request, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.middleware.db_session import get_db_session
from app.middleware.depends import validate_token_by_role
from app.enum.user import UserRole
from app.util.auth import JwtPayload, decode_jwt
from app.db.operator.book import get_books, get_book_with_details
from app.router.template.index import templates

router = APIRouter()

# Helper to get current user optionally (for displaying "Welcome, User" or login button)
async def get_current_user_optional(request: Request) -> Optional[JwtPayload]:
    token = request.cookies.get("auth_token")
    if not token:
        return None
    try:
        return decode_jwt(token)
    except:
        return None

@router.get("/books")
async def list_books_page(
    request: Request,
    keyword: Optional[str] = Query(None, description="Search keyword"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Page to list all books with search functionality.
    """
    books = await get_books(db=db, keyword=keyword, category=category)
    user = await get_current_user_optional(request)

    context = {
        "request": request,
        "books": books,
        "keyword": keyword or "",
        "user": user,
    }
    
    return templates.TemplateResponse(
        "/product/list.jinja", context=context, status_code=status.HTTP_200_OK
    )


@router.get("/books/{book_id}")
async def book_detail_page(
    request: Request,
    book_id: UUID,
    db: AsyncSession = Depends(get_db_session),
):
    """
    Page to show detailed info of a book and list of bookstores selling it.
    """
    book = await get_book_with_details(db=db, book_id=book_id)
    user = await get_current_user_optional(request)

    error_message = None
    if not book:
        error_message = "Book not found."

    context = {
        "request": request,
        "book": book,
        "user": user,
        "error": error_message
    }

    return templates.TemplateResponse(
        "/product/detail.jinja", context=context, status_code=status.HTTP_200_OK
    )
    

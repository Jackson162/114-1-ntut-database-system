from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from app.middleware.db_session import get_db_session
from pathlib import Path

from app.db.operator.cart import get_cart_item_count
from app.db.operator.book import get_all_categories, get_new_arrivals
from app.util.auth import decode_jwt


router = APIRouter()

ROUTER_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = ROUTER_DIR / "template"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

@router.get("/home")
async def customer_homepage(
    request: Request,
    db: Session = Depends(get_db_session),
):
    token = request.cookies.get("auth_token")
    payload = decode_jwt(token)
    customer_account = payload.account


    cart_count = await get_cart_item_count(db, customer_account)
    categories = await get_all_categories(db)
    new_books = await get_new_arrivals(db)

    return templates.TemplateResponse(
        "customer/home.jinja",
        {
            "request": request,
            "cart_count": cart_count,
            "categories": categories,
            "new_arrivals": [
                {
                    "book_id": b.book_id,
                    "title": b.title,
                    "author": b.author,
                    "image_url": "https://placehold.co/180x120",
                    "min_price": None,
                }
                for b in new_books
            ],
            "bestsellers": [],
            "promotions": [],
        },
    )

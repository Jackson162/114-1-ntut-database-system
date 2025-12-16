from typing import Tuple, Optional
from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from app.middleware.depends import validate_token_by_role
from app.middleware.db_session import get_db_session
from app.enum.user import UserRole
from app.db.models.customer import Customer
from app.db.operator.bookstore import get_bookstore_by_id
from app.util.auth import JwtPayload
from app.router.template.index import templates
from app.router.schema.sqlachemy import BookstoreSchema
from app.logging.logger import get_logger

logger = get_logger()

router = APIRouter()

validate_staff_token = validate_token_by_role(UserRole.STAFF)


@router.get("/bookstores")
async def get_staff_bookstore(
    request: Request,
    create_staff_bookstore_error: Optional[str] = None,
    login_data: Tuple[JwtPayload, Customer] = Depends(validate_staff_token),
    db: AsyncSession = Depends(get_db_session),
):
    _, staff = login_data

    get_staff_bookstore_error = ""

    try:
        bookstore = await get_bookstore_by_id(db=db, bookstore_id=staff.bookstore_id)
        bookstore_dict = BookstoreSchema.from_orm(bookstore).dict()
    except NoResultFound:
        bookstore_dict = None
    except Exception as err:
        logger.error(err)
        get_staff_bookstore_error = repr(err)
        bookstore_dict = None

    context = {
        "request": request,
        "bookstore": bookstore_dict,
        "get_staff_bookstore_error": get_staff_bookstore_error,
        "create_staff_bookstore_error": None,
    }

    if create_staff_bookstore_error:
        context["create_staff_bookstore_error"] = create_staff_bookstore_error

    return templates.TemplateResponse(
        "/staff/bookstore.jinja", context=context, status_code=status.HTTP_200_OK
    )

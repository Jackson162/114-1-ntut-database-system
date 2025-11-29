from typing import Tuple

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.util.auth import JwtPayload, decode_jwt
from app.middleware.db_session import get_db_session
from app.db.models.admin import Admin
from app.db.models.customer import Customer
from app.db.models.staff import Staff
from app.enum.user import UserRole
from app.db.operator.admin import get_admin_by_account
from app.db.operator.customer import get_customer_by_account
from app.db.operator.staff import get_staff_by_account

oauth2_schema = OAuth2PasswordBearer("auth/login")


def validate_token_by_role(authorized_role: str):
    async def aux(
        token: str = Depends(oauth2_schema),
        db: AsyncSession = Depends(get_db_session),
    ) -> Tuple[JwtPayload, Customer] | Tuple[JwtPayload, Staff] | Tuple[JwtPayload, Admin]:
        try:
            jwt_payload = decode_jwt(token)

            if jwt_payload.role != authorized_role:
                raise Exception(f"Authorized role is {authorized_role} but got {jwt_payload.role}")

            if jwt_payload.role == UserRole.ADMIN:
                user = await get_admin_by_account(db=db, account=jwt_payload.account)
            elif jwt_payload.role == UserRole.CUSTOMER:
                user = await get_customer_by_account(db=db, account=jwt_payload.account)
            elif jwt_payload.role == UserRole.STAFF:
                user = await get_staff_by_account(db=db, account=jwt_payload.account)
            else:
                raise Exception(
                    f"Role: {jwt_payload.role} with account: {jwt_payload.account} does not exist"
                )
            return jwt_payload, user
        except Exception as err:
            raise err

    return aux

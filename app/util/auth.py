import jwt
import bcrypt
from app.util.schema.auth import JwtPayload
from app.core.config import settings


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def encode_jwt(payload: JwtPayload) -> str:
    """Encode JWT payload."""
    encoded_jwt = jwt.encode(
        payload.dict(), settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt

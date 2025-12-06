from datetime import datetime as dt, timedelta

import jwt
import bcrypt
from app.util.schema.auth import JwtPayload
from app.core.config import settings
from app.logging.logger import get_logger

logger = get_logger()


def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def validate_password(password: str, hashed_password: str) -> bool:
    password_bytes = password.encode("utf-8")
    hashed_password_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_password_bytes)


def generate_jwt(
    account: str,
    role: str,
    expires_in_seconds: int = 86400 * 30,
) -> str:
    """Generate an encoded JWT."""
    issued_at = dt.now()
    expired_at = issued_at + timedelta(seconds=expires_in_seconds)
    payload = JwtPayload(
        iss=settings.JWT_ISSUER,
        account=account,
        role=role,
        iat=int(issued_at.timestamp()),
        exp=int(expired_at.timestamp()),
    )
    logger.info(
        f"[generate_jwt] start encoding jwt: payload: {payload},"
        f" algorithm: {settings.JWT_ALGORITHM}"
    )
    return encode_jwt(payload)


def encode_jwt(payload: JwtPayload) -> str:
    """Encode JWT payload."""
    encoded_jwt = jwt.encode(
        payload.dict(), settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_jwt(
    token: str,
) -> JwtPayload:
    """
    options: Decoding options. If omitted, the default options is:

        {
            "verify_signature": True,
            "verify_exp": True,
            "verify_nbf": True,
            "verify_iat": True,
            "verify_aud": True,
            "verify_iss": True,
            "require": [],
        }

    """
    try:
        payload = jwt.decode(
            token,
            key=settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            issuer=settings.JWT_ISSUER,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_iat": True,
                "verify_iss": True,
            },
        )

        return JwtPayload(**payload)
    except jwt.DecodeError as err:
        logger.error(f"Failed to decode JWT token:{token}, error:{err}")
        raise err
    except (
        jwt.ExpiredSignatureError,
        jwt.ImmatureSignatureError,
        jwt.InvalidSignatureError,
        jwt.InvalidTokenError,
    ) as err:
        logger.error(f"Invalid JWT token:{token}, error:{err}")
        raise err

from pydantic import BaseModel, Field


class JwtPayload(BaseModel):
    """JwtPayload"""

    iss: str = Field(
        ...,
        title="iss",
        description="Issuer",
    )
    iat: int = Field(
        ...,
        title="iat",
        description="The time at the jwt was issued",
        example=1652836275,
    )
    exp: int = Field(
        ...,
        title="exp",
        description="Expiration time",
        example=1652837133,
    )
    account: str = Field(
        ...,
        title="account",
        description="The account of this user",
        example="tomhanks123",
    )
    role: str = Field(
        ...,
        title="role",
        description="The role of this user",
        example="admin",
    )

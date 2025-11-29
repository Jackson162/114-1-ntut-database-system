from pydantic import BaseModel, Field


class LoginData(BaseModel):
    """User schema base for inherit."""

    role: str = Field(..., title="role", description="The role of a user", example="admin")
    account: str = Field(
        ..., title="account", description="The account of a user", example="satoshi"
    )
    password: str = Field(
        ..., title="password", description="The password of a user", example="1234"
    )

    class Config:
        """Enable orm_mode."""

        orm_mode = True

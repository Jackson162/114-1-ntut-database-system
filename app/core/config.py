from typing import Any, Dict, Optional, Union

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """Extract env variables to app settings."""

    # database
    # enable this if you want to build a new db in your local
    DO_INIT_DB: bool = False
    POSTGRES_HOST: str
    POSTGRES_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URI: Union[PostgresDsn, str] = ""
    DB_POOL_SIZE: int = 40
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(
        cls, v: Optional[str], values: Dict[str, Any]
    ) -> Union[PostgresDsn, str]:
        """Assemble db connection uri if no DATABASE_URI env variables."""
        if v:
            return v
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_HOST"),  # type: ignore
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    class Config:  # type: ignore
        case_sensitive = True
        env_file = ".env"


settings = Settings()  # type: ignore

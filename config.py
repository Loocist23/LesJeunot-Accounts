from dataclasses import dataclass
from os import getenv
from secrets import token_hex
from urllib.parse import quote_plus

from dotenv import load_dotenv


load_dotenv(".env")


@dataclass(slots=True)
class Settings:
    """Central application configuration loaded from the environment."""

    host: str = getenv("HOST", "127.0.0.1")
    port: int = int(getenv("PORT", "5000"))
    secret_key: str = getenv("SECRET_KEY", token_hex(32))
    jwt_secret_key: str = getenv("JWT_SECRET_KEY", token_hex(32))
    jwt_issuer: str = getenv("JWT_ISSUER", "")

    db_host: str = getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(getenv("DB_PORT", "3306"))
    db_name: str = getenv("DB_NAME", "lesjeunot")
    db_user: str = getenv("DB_USER", "root")
    db_password: str = getenv("DB_PASSWORD", "")
    cors_origins: str = getenv("CORS_ORIGINS", "*")

    @property
    def database_url(self) -> str:
        """Build a SQLAlchemy-compatible MySQL connection string."""
        password = quote_plus(self.db_password)
        return (
            f"mysql+pymysql://{self.db_user}:{password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

from typing import Optional
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    database_url: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    name: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        if self.user and self.password and self.host and self.port and self.name:
            return f"postgresql+psycopg://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"
        raise ValueError("No database URL configured. Set DATABASE_URL or DB_* environment variables.")

    model_config = {
        "env_prefix": "DB_",
        "env_file": ".env",
        "extra": "ignore",
    }


db_settings = DatabaseSettings()
from pydantic_settings import BaseSettings


class CrossrefSettings(BaseSettings):
    email: str = ""
    password: str = ""

    model_config = {
        "env_file": ".env",
        "extra": "ignore",
    }


_settings = CrossrefSettings()
EMAIL = _settings.email
PASSWORD = _settings.password
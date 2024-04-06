import pytz
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytz.tzinfo import StaticTzInfo


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    DEBUG: bool = True

    BOT_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str = ""

    TG_TOKEN: str

    @computed_field  # type: ignore[misc]
    @property
    def tz_info(self) -> StaticTzInfo:
        return pytz.timezone("Asia/Yekaterinburg")


settings = Settings()  # type: ignore

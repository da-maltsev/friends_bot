import locale
from datetime import datetime

import pytz
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pytz.tzinfo import StaticTzInfo

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


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

    def tz_now(self) -> datetime:
        return datetime.now(tz=self.tz_info)


settings = Settings()  # type: ignore

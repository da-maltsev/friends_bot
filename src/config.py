from pydantic import RedisDsn, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    @computed_field
    def redis_dsn(self) -> RedisDsn:
        return RedisDsn.build(
            scheme="redis",
            password=self.REDIS_PASSWORD,
            host=self.REDIS_HOST,
            port=self.REDIS_PORT,
        )


settings = Settings()  # type: ignore

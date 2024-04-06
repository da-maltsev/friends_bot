from contextlib import asynccontextmanager
from enum import Enum, auto
from string import Template
from typing import Any, AsyncGenerator

import redis.asyncio as redis
from config import settings

client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, password=settings.REDIS_PASSWORD)


@asynccontextmanager
async def redis_connection() -> AsyncGenerator[redis.Redis, None]:
    try:
        yield client
    finally:
        await client.aclose()


class KeysEnum(str, Enum):
    meeting = auto()
    chat_info = auto()
    meeting_list = auto()


KEY_TEMPLATES: dict[KeysEnum, Template] = {
    KeysEnum.chat_info: Template("${chat_id}-chat_info"),
    KeysEnum.meeting: Template("${chat_id}-meetings-${meeting_id}"),
    KeysEnum.meeting_list: Template("${chat_id}-meeting_list"),
}


def get_redis_key(key: KeysEnum, **kwargs: Any) -> str:
    return KEY_TEMPLATES[key].substitute(**kwargs)


__all__ = (
    "redis_connection",
    "get_redis_key",
    "KeysEnum",
)

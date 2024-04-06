from typing import cast

from db import KeysEnum, get_redis_key
from extra_types import MessageText
from models import ChatGroup
from redis.asyncio import Redis
from telegram import Chat, Message, Update


def cast_defaults(update: Update) -> tuple[Chat, Message, MessageText]:
    effective_chat = cast("Chat", update.effective_chat)
    message = cast("Message", update.message)
    in_text = cast(MessageText, message.text)
    return effective_chat, message, in_text


async def check_auth(chat_id: str | int, redis: Redis) -> bool:
    redis_key = get_redis_key(KeysEnum.chat_info, chat_id=chat_id)
    chat_info_raw = await redis.get(redis_key)
    return chat_info_raw and ChatGroup(**chat_info_raw).is_logged

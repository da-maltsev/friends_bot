from string import Template
from typing import cast

from db import KeysEnum, get_redis_key
from extra_types import MessageText
from redis.asyncio import Redis
from telegram import CallbackQuery, Chat, Message, Update, User

EXPECTED_FORMAT = Template("Неверный формат ввода, ожидаемый формат:\n ${expected}")


def cast_defaults_command(update: Update) -> tuple[Chat, Message, MessageText, User]:
    effective_chat = cast("Chat", update.effective_chat)
    message = cast("Message", update.message)
    in_text = cast(MessageText, message.text)
    user = cast("User", message.from_user)
    return effective_chat, message, in_text, user


def cast_defaults_callback(update: Update) -> tuple[Chat, CallbackQuery, Message, str, User]:
    effective_chat = cast("Chat", update.effective_chat)
    query = cast("CallbackQuery", update.callback_query)
    message = cast("Message", query.message)
    data = cast(str, query.data)
    return effective_chat, query, message, data, query.from_user


async def check_auth(chat_id: str | int, message: Message, redis: Redis) -> bool:
    from models import ChatGroup

    redis_key = get_redis_key(KeysEnum.chat_info, chat_id=chat_id)
    chat_info_raw = await redis.get(redis_key)
    if not chat_info_raw or not ChatGroup.model_validate_json(chat_info_raw).is_logged:
        await message.reply_text("Я бот для друзей. Введи пароль по схеме '/start password', чтобы продолжить.")
        return False
    return True


def safe_str(obj: object, attr: "str") -> str:
    return getattr(obj, attr, None) or ""

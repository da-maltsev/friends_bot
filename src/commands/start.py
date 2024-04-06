from config import settings
from db import KeysEnum, get_redis_key, redis_connection
from models import ChatGroup
from telegram import Update
from telegram.ext import ContextTypes
from utils import cast_defaults, check_auth


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    effective_chat, message, in_text = cast_defaults(update)
    redis_key = get_redis_key(KeysEnum.chat_info, chat_id=effective_chat.id)

    async with redis_connection() as redis:
        if in_text.split(" ")[-1] == settings.BOT_PASSWORD:
            text = "Авторизация прошла успешно! Можем продолжать."
            is_logged = True
        else:
            is_logged = await check_auth(effective_chat.id, redis)
            if not is_logged:
                text = "Я бот для друзей. Введи пароль по схеме '/start password', чтобы продолжить."
            else:
                text = "Привет! Авторизация уже пройдена, можем продолжить."

        new_chat_info = ChatGroup(
            chat_id=effective_chat.id,
            is_logged=is_logged,
        )
        await redis.set(redis_key, new_chat_info.model_dump_json())

    await context.bot.send_message(chat_id=effective_chat.id, text=text)

from abc import ABC, abstractmethod

from db import redis_connection
from extra_types import MessageText
from redis.asyncio import Redis
from telegram import Chat, Message, Update
from telegram.ext import ContextTypes
from utils import cast_defaults, check_auth


class BaseCommand(ABC):
    """
    Стандартный класс для добавления команды в бота.
    Для создания команды нужно наследоваться от данного класса и переопределить метод act.
    Для регистрации команды нужно в __init__.py в registry добавить новую команду следующим образом:
    registry = (
        ...
        CommandHandler("new_command_name", NewCommand.run),
    )
    """

    @classmethod
    async def run(cls, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        effective_chat, message, text = cast_defaults(update)

        async with redis_connection() as redis:
            is_logged = await check_auth(effective_chat.id, redis)
            if is_logged:
                await cls.act(update, context, effective_chat, message, text, redis)
            else:
                await context.bot.send_message(
                    chat_id=effective_chat.id,
                    text="Вы не авторизованы. Введите пароль по схеме '/.start password'",
                )

    @classmethod
    @abstractmethod
    async def act(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        chat: Chat,
        message: Message,
        text: MessageText,
        redis: Redis,
    ) -> None:
        return

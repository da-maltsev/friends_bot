from config import settings
from db import KeysEnum, get_redis_key, redis_connection
from handlers.const import MAIN_MENU_KEYBOARD
from models import ChatGroup
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils import cast_defaults_command, check_auth


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда для авторизации и начала взаимодействия с ботом"""
    effective_chat, message, in_text, _ = cast_defaults_command(update)
    redis_key = get_redis_key(KeysEnum.chat_info, chat_id=effective_chat.id)

    async with redis_connection() as redis:
        if in_text.split(" ")[-1] == settings.BOT_PASSWORD:
            text = "Авторизация прошла успешно! Можем продолжать."
            is_logged = True
        else:
            is_logged = await check_auth(effective_chat.id, message, redis)

        new_chat_info = ChatGroup(
            chat_id=effective_chat.id,
            is_logged=is_logged,
        )
        await redis.set(redis_key, new_chat_info.model_dump_json())

    if is_logged:
        await context.bot.send_message(chat_id=effective_chat.id, text=text)


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Выводит справку по командам"""
    from handlers import commands

    _, message, _, _ = cast_defaults_command(update)
    texts = []
    i = 0
    for handler in commands:
        if (docstring := getattr(handler.callback, "__doc__", None)) is None:
            continue
        i += 1
        texts.append(f"{i}. Команда /{next(iter(handler.commands))}: {docstring}.\n")

    await message.reply_text("".join(texts))


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Главное меню бота с основным функционалом"""
    effective_chat, message, in_text, _ = cast_defaults_command(update)

    keyboard = InlineKeyboardMarkup(inline_keyboard=MAIN_MENU_KEYBOARD)
    await message.reply_text("Что хочешь?", reply_markup=keyboard)

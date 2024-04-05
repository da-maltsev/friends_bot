from config import settings
from telegram import Update
from telegram.ext import ContextTypes
from utils import cast_defaults


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    effective_chat, message, in_text = cast_defaults(update)

    text = "Я бот для друзей. Введи пароль по схеме '/start password', чтобы продолжить."
    if settings.IS_LOGGED_IN:
        text = "Привет! Авторизация уже пройдена, можем продолжить"
    elif in_text.split(" ")[-1] == settings.BOT_PASSWORD:
        settings.IS_LOGGED_IN = True
        text = "Авторизация прошла успешно! Можем продолжать"
    await context.bot.send_message(chat_id=effective_chat.id, text=text)

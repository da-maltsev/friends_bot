from const import GlobalCallbackEnum
from db import redis_connection
from handlers.const import CallbackEnum, parse_callback
from handlers.meeting import CALLBACK_MAPPING
from telegram import Update
from telegram.ext import ContextTypes
from utils import cast_defaults_callback


async def keyboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat, query, message, data, user = cast_defaults_callback(update)
    if data == GlobalCallbackEnum.close:
        await message.delete()
        return

    callback_type, body = parse_callback(data)
    if (act := CALLBACK_MAPPING.get(CallbackEnum(callback_type))) is not None:
        async with redis_connection() as redis:
            act = CALLBACK_MAPPING[CallbackEnum(callback_type)]
            await act(chat, message, body, user, redis)


async def close(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat, query, message, data, user = cast_defaults_callback(update)
    if data == GlobalCallbackEnum.close:
        await message.delete()

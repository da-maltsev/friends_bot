from const import GlobalCallbackEnum
from db import redis_connection
from extra_types import Callback, DetailedCallback
from handlers.const import MAIN_MENU_KEYBOARD, CallbackEnum, DetailedCallbackEnum
from handlers.mappings import get_common_callback, get_detailed_callback
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from utils import cast_defaults_callback


async def keyboard_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat, query, message, data, user = cast_defaults_callback(update)
    if data == GlobalCallbackEnum.close:
        await message.delete()
        return
    if data == GlobalCallbackEnum.main_menu:
        await message.edit_text("Что хочешь?", reply_markup=InlineKeyboardMarkup(MAIN_MENU_KEYBOARD))
        return

    async with redis_connection() as redis:
        match data.split("|"):
            case (callback_type,):
                act: Callback = get_common_callback(CallbackEnum(callback_type))
                await act(chat, message, user, redis)
                return
            case (callback_type, entity_id):
                detailed_act: DetailedCallback = get_detailed_callback(DetailedCallbackEnum(callback_type))
                await detailed_act(chat, message, user, redis, entity_id)

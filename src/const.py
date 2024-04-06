from enum import Enum, auto

from telegram import InlineKeyboardButton


class GlobalCallbackEnum(str, Enum):
    close = auto()
    main_menu = auto()


BASE_INLINE: list[list[InlineKeyboardButton]] = [
    [
        InlineKeyboardButton(
            text="Закрыть меню",
            callback_data=GlobalCallbackEnum.close.value,
        )
    ],
    [
        InlineKeyboardButton(
            text="В главное меню",
            callback_data=GlobalCallbackEnum.main_menu.value,
        )
    ],
]

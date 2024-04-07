from enum import Enum, auto

from telegram import InlineKeyboardButton


class CallbackEnum(str, Enum):
    add_meeting = "Добавить мероприятие"
    list_meetings = "Посмотреть список мероприятий"
    participate_meeting = "Участвовать в мероприятии"
    leave_meeting = "Отказаться от участия"
    retrieve_meeting = "Подробнее о встрече"
    delete_meeting = "Отменить встречу"


class DetailedCallbackEnum(str, Enum):
    participate_meeting_id = auto()
    leave_meeting_id = auto()
    retrieve_meeting_id = auto()
    delete_meeting_id = auto()


MAIN_MENU_KEYBOARD = [
    [
        InlineKeyboardButton(
            text=callback_type,
            callback_data=callback_type,
        )
    ]
    for callback_type in CallbackEnum
    if callback_type != CallbackEnum.retrieve_meeting
]

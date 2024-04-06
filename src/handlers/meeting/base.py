from abc import ABC, abstractmethod
from typing import cast

from const import BASE_INLINE
from db import KeysEnum, get_redis_key
from extra_types import MessageText
from handlers.base_command import BaseCommand
from handlers.const import CALLBACK_TEMPLATE, CallbackEnum
from models import MeetingList, Participant
from redis.asyncio import Redis
from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup, Message, Update, User
from telegram.ext import ContextTypes


class BaseMeetingCommand(BaseCommand, ABC):
    @classmethod
    async def get_meetings_list(cls, redis: Redis, chat_id: int) -> MeetingList:
        redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat_id)
        meeting_list_raw = await redis.get(redis_key)
        meeting_list = MeetingList()  # type: ignore[call-arg]
        if meeting_list_raw:
            meeting_list = MeetingList.model_validate_json(meeting_list_raw)
            meeting_list = meeting_list.filter_outdated()
        return meeting_list


class BaseParticipateMeetingCommand(BaseMeetingCommand, ABC):
    @classmethod
    async def act(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        chat: Chat,
        message: Message,
        text: MessageText,
        user: User,
        redis: Redis,
    ) -> None:
        meeting_list = await cls.get_meetings_list(redis, chat.id)
        as_participant = Participant.from_user(user)
        callback_type = cast("CallbackEnum", cls.CALLBACK_TYPE)

        meetings_as_buttons = [
            [
                InlineKeyboardButton(
                    text=meeting.as_button(),
                    callback_data=CALLBACK_TEMPLATE[callback_type].substitute(meeting_id=meeting.id),
                )
            ]
            for meeting in meeting_list.meetings.values()
            if (as_participant not in meeting.participants and callback_type == CallbackEnum.meeting_participate)
            or (as_participant in meeting.participants and callback_type == CallbackEnum.meeting_leave)
        ]
        meetings_as_buttons = [*BASE_INLINE, *meetings_as_buttons]
        keyboard = InlineKeyboardMarkup(inline_keyboard=meetings_as_buttons)
        await message.reply_text(str(cls.MESSAGE), reply_markup=keyboard)

    @classmethod  # type: ignore[misc]
    @property
    @abstractmethod
    def MESSAGE(cls) -> str: ...

    @classmethod  # type: ignore[misc]
    @property
    @abstractmethod
    def CALLBACK_TYPE(cls) -> CallbackEnum: ...

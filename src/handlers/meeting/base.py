import asyncio
from abc import ABC, abstractmethod
from uuid import UUID

from db import KeysEnum, get_redis_key
from extra_types import MessageText
from handlers.base_command import BaseCommand, CommandException
from models import Meeting, MeetingList, Participant
from redis.asyncio import Redis
from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes
from utils import EXPECTED_FORMAT


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
        meeting_id = cls.get_meeting_id(text)
        meeting_list = await cls.get_meetings_list(redis, chat.id)
        as_participant = Participant.from_user(user)

        meeting = cls.get_meeting(meeting_list, meeting_id)
        cls.special_act(meeting, as_participant)

        redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat.id)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(redis.set(redis_key, meeting_list.model_dump_json()))  # type: ignore[arg-type]
            tg.create_task(message.reply_text(f"Встреча обновлена: \n{meeting}"))

    @classmethod
    def get_meeting_id(cls, text: str) -> UUID:
        raw = text.split(" ")[-1]
        try:
            return UUID(raw)
        except ValueError:
            raise CommandException(EXPECTED_FORMAT.substitute(expected=cls.FORMAT))

    @classmethod
    def get_meeting(cls, meeting_list: MeetingList, meeting_id: UUID) -> Meeting:
        meeting = meeting_list.meetings.get(meeting_id)
        if not meeting:
            raise CommandException(f"Нет встречи с ID: {meeting_id}")
        return meeting

    @classmethod
    @abstractmethod
    def special_act(cls, meeting: Meeting, as_participant: Participant) -> None: ...

    @classmethod  # type: ignore[misc]
    @property
    @abstractmethod
    def FORMAT(cls) -> str: ...

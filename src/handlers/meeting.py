import asyncio
from datetime import datetime
from enum import Enum
from uuid import UUID

from config import settings
from db import KeysEnum, get_redis_key
from extra_types import Location, MessageText
from handlers.base_command import BaseCommand, CommandException
from models import Meeting, MeetingList, Participant
from redis.asyncio import Redis
from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes
from utils import EXPECTED_FORMAT

__all__ = (
    "AddMeetingCommand",
    "ListMeetingCommand",
    "ParticipateMeetingCommand",
)


async def get_meetings_list(redis: Redis, chat_id: int) -> MeetingList:
    redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat_id)
    meeting_list_raw = await redis.get(redis_key)
    meeting_list = MeetingList()  # type: ignore[call-arg]
    if meeting_list_raw:
        meeting_list = MeetingList.model_validate_json(meeting_list_raw)
        meeting_list = meeting_list.filter_outdated()
    return meeting_list


class PlanMeetingEnum(Enum):
    today = "Сегодня"
    this_week = "На этой неделе"
    next_week = "На следующей неделе"
    this_month = "В этом месяце"


class ListMeetingCommand(BaseCommand):
    """Команда для получения списка встреч"""

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
        redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat.id)
        meeting_list = await get_meetings_list(redis, chat.id)
        out_text = str(meeting_list) if len(meeting_list.meetings) > 0 else "Список встреч пуст"

        async with asyncio.TaskGroup() as tg:
            if meeting_list:
                tg.create_task(redis.set(redis_key, meeting_list.model_dump_json()))  # type: ignore[arg-type]
            tg.create_task(message.reply_text(out_text))


class AddMeetingCommand(BaseCommand):
    """Команда для создания встречи"""

    FORMAT = "/plan_add |Название|05-05-2005 15:55|Бар Лавкрафт"

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
        try:
            _, title, datetime_string, location = text.split("|")
            initiator = Participant.from_user(user)
            new_meeting = Meeting(  # type: ignore[call-arg]
                date=cls.get_date_from_string(datetime_string),
                title=title,
                location=Location(location),
                initiator=initiator,
            )
        except (TypeError, ValueError):
            await message.reply_text(EXPECTED_FORMAT.substitute(expected=cls.FORMAT))
            return

        meeting_list = await get_meetings_list(redis, chat.id)
        upd_meeting_list = cls.add_meeting(meeting_list, new_meeting)
        redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat.id)

        async with asyncio.TaskGroup() as tg:
            tg.create_task(redis.set(redis_key, upd_meeting_list.model_dump_json()))  # type: ignore[arg-type]
            tg.create_task(message.reply_text(f"Встреча запланирована: \n{new_meeting}"))

    @classmethod
    def add_meeting(cls, meetings_list: MeetingList, new_meeting: Meeting) -> MeetingList:
        if meetings_list.check_new_meeting_in_list(new_meeting):
            raise CommandException(f"Такая встреча уже запланирована: \n{new_meeting}")
        meetings_list.meetings.update({new_meeting.id: new_meeting})
        return meetings_list

    @classmethod
    def get_date_from_string(cls, datetime_str: str) -> datetime:
        date = datetime.strptime(datetime_str, "%d-%m-%Y %H:%M").replace(tzinfo=settings.tz_info)
        if date < datetime.now(tz=settings.tz_info):
            raise CommandException(f"Введена уже прошедшая дата: {datetime_str}")
        return date


class ParticipateMeetingCommand(BaseCommand):
    """Команда для добавления пользователя как участника встречи"""

    FORMAT = "/part_plan id-встречи"

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
        meeting_list = await get_meetings_list(redis, chat.id)
        as_participant = Participant.from_user(user)

        meeting = cls.get_meeting(meeting_list, meeting_id)
        meeting.participants.add(as_participant)

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

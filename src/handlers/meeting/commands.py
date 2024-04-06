import asyncio
from datetime import datetime

from config import settings
from db import KeysEnum, get_redis_key
from extra_types import Location, MessageText
from handlers.base_command import CommandException
from handlers.const import CallbackEnum
from handlers.meeting.base import BaseMeetingCommand, BaseParticipateMeetingCommand
from models import Meeting, MeetingList, Participant
from redis.asyncio import Redis
from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes
from utils import EXPECTED_FORMAT


class ListMeetingCommand(BaseMeetingCommand):
    """Команда для получения списка встреч"""

    COMMAND = "plan_list"

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
        meeting_list = await cls.get_meetings_list(redis, chat.id)
        out_text = str(meeting_list) if len(meeting_list.meetings) > 0 else "Список встреч пуст"

        async with asyncio.TaskGroup() as tg:
            if meeting_list:
                tg.create_task(redis.set(redis_key, meeting_list.model_dump_json()))  # type: ignore[arg-type]
            tg.create_task(message.reply_text(out_text))


class AddMeetingCommand(BaseMeetingCommand):
    """Команда для создания встречи"""

    COMMAND = "plan_add"
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

        meeting_list = await cls.get_meetings_list(redis, chat.id)
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


class ParticipateMeetingCommand(BaseParticipateMeetingCommand):
    """Команда для добавления пользователя как участника встречи"""

    COMMAND = "plan_part"
    CALLBACK_TYPE = CallbackEnum.meeting_participate
    MESSAGE = "Выбери, куда придешь:"


class LeaveMeetingCommand(BaseParticipateMeetingCommand):
    """Команда для удаления пользователя как участника встречи"""

    COMMAND = "plan_leave"
    CALLBACK_TYPE = CallbackEnum.meeting_leave
    MESSAGE = "Выбери, куда не придешь:"

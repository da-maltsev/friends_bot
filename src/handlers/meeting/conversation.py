import asyncio
import calendar
from datetime import datetime

from config import settings
from db import TEN_MINUTES, KeysEnum, get_redis_key, redis_connection
from extra_types import Location
from handlers.meeting.const import AddMeetingEnum, MeetingLocationEnum, MeetingTypesEnum
from handlers.meeting.utils import add_meeting_in_meeting_list, get_meetings_list
from models import Meeting, MeetingList, Participant
from pydantic import ValidationError
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from utils import cast_defaults_command


async def add_meeting(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMeetingEnum:
    """Starts the conversation and asks the user about their gender."""
    effective_chat, message, in_text, user = cast_defaults_command(update)
    reply_keyboard = []
    row: list = []
    for meeting_type in MeetingTypesEnum:
        if len(row) == 2:
            reply_keyboard.append(row)
            row = []
        row.append(meeting_type)
    if row:
        reply_keyboard.append(row)

    redis_key = get_redis_key(KeysEnum.new_meeting, chat_id=effective_chat.id)
    new_meeting = Meeting(  # type: ignore[call-arg]
        initiator=Participant.from_user(user),
        date=datetime.now(tz=settings.tz_info),
        title="",
        location=Location(""),
    )

    async with redis_connection() as redis, asyncio.TaskGroup() as tg:
        tg.create_task(
            message.reply_text(
                "Давай выберем тему, либо можешь написать свой вариант и отправить. Если передумал, используй /cancel",
                reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Какая тема?"),
            )
        )
        tg.create_task(redis.set(redis_key, new_meeting.model_dump_json(), ex=TEN_MINUTES))  # type: ignore[arg-type]

    return AddMeetingEnum.title


async def meeting_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMeetingEnum:
    effective_chat, message, in_text, user = cast_defaults_command(update)
    new_title = in_text

    reply_keyboard = []
    row: list = []
    for month in calendar.month_name[1:]:
        if datetime.strptime(month, "%B").replace(tzinfo=settings.tz_info).month < datetime.now(tz=settings.tz_info).month:
            continue
        if len(row) == 2:
            reply_keyboard.append(row)
            row = []
        row.append(month)
    if row:
        reply_keyboard.append(row)

    redis_key = get_redis_key(KeysEnum.new_meeting, chat_id=effective_chat.id)
    async with redis_connection() as redis:
        new_meeting = Meeting.model_validate_json(await redis.get(redis_key))
        new_meeting.title = new_title
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                message.reply_text(
                    "Давай выберем месяц. Если передумал, используй /cancel",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="В каком месяце?"),
                )
            )
            tg.create_task(redis.set(redis_key, new_meeting.model_dump_json(), ex=TEN_MINUTES))  # type: ignore[arg-type]

    return AddMeetingEnum.month


async def meeting_day(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMeetingEnum:
    effective_chat, message, in_text, user = cast_defaults_command(update)
    new_date = datetime.strptime(in_text, "%B").replace(tzinfo=settings.tz_info)
    new_month = new_date.month
    num_days = calendar.monthrange(datetime.now(tz=settings.tz_info).year, new_month)[1]

    reply_keyboard = []
    row: list = []
    for day in range(1, num_days + 1):
        if new_month == datetime.now(tz=settings.tz_info).month and day < datetime.now(tz=settings.tz_info).day:
            continue
        if len(row) == 6:
            reply_keyboard.append(row)
            row = []
        row.append(str(day))
    if row:
        reply_keyboard.append(row)

    redis_key = get_redis_key(KeysEnum.new_meeting, chat_id=effective_chat.id)
    async with redis_connection() as redis:
        new_meeting = Meeting.model_validate_json(await redis.get(redis_key))
        new_meeting.date = new_meeting.date.replace(month=new_month)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                message.reply_text(
                    f"Давай выберем в какой день {in_text}. Если передумал, используй /cancel",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="В какой день месяца?"),
                )
            )
            tg.create_task(redis.set(redis_key, new_meeting.model_dump_json(), ex=TEN_MINUTES))  # type: ignore[arg-type]
    return AddMeetingEnum.day


async def meeting_hour(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMeetingEnum:
    effective_chat, message, in_text, user = cast_defaults_command(update)
    new_day = int(in_text)

    reply_keyboard = [
        ["10", "11", "12", "13", "14"],
        ["15", "16", "17", "18", "19"],
        ["20", "21", "22", "23"],
    ]

    redis_key = get_redis_key(KeysEnum.new_meeting, chat_id=effective_chat.id)
    async with redis_connection() as redis:
        new_meeting = Meeting.model_validate_json(await redis.get(redis_key))
        new_meeting.date = new_meeting.date.replace(day=new_day)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                message.reply_text(
                    f"Давай выберем в какой час {new_meeting.date.strftime('%d-%m')}. Если передумал, используй /cancel",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="В какой час?"),
                )
            )
            tg.create_task(redis.set(redis_key, new_meeting.model_dump_json(), ex=TEN_MINUTES))  # type: ignore[arg-type]

    return AddMeetingEnum.hour


async def meeting_minute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMeetingEnum:
    effective_chat, message, in_text, user = cast_defaults_command(update)
    new_hour = int(in_text)

    reply_keyboard = [
        ["00", "05", "10", "15"],
        ["20", "25", "30", "35"],
        ["40", "45", "50", "55"],
    ]

    redis_key = get_redis_key(KeysEnum.new_meeting, chat_id=effective_chat.id)
    async with redis_connection() as redis:
        new_meeting = Meeting.model_validate_json(await redis.get(redis_key))
        new_meeting.date = new_meeting.date.replace(hour=new_hour, minute=55)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                message.reply_text(
                    f"Давай уточним минуты начала {new_meeting.date.strftime('%d-%m, %H')}. Если передумал, используй /cancel",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Во сколько минут начнем?"),
                )
            )
            tg.create_task(redis.set(redis_key, new_meeting.model_dump_json(), ex=TEN_MINUTES))  # type: ignore[arg-type]

    return AddMeetingEnum.minute


async def meeting_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AddMeetingEnum:
    effective_chat, message, in_text, user = cast_defaults_command(update)
    new_minute = int(in_text)

    reply_keyboard = []
    row: list = []
    for location in MeetingLocationEnum:
        if len(row) == 2:
            reply_keyboard.append(row)
            row = []
        row.append(location)
    if row:
        reply_keyboard.append(row)

    redis_key = get_redis_key(KeysEnum.new_meeting, chat_id=effective_chat.id)
    async with redis_connection() as redis:
        new_meeting = Meeting.model_validate_json(await redis.get(redis_key))
        new_meeting.date = new_meeting.date.replace(minute=new_minute)
        async with asyncio.TaskGroup() as tg:
            tg.create_task(
                message.reply_text(
                    f"А где встретимся {new_meeting.date.strftime('%d-%m, %H:%M')}? Можешь ввести свой вариант. Если передумал, используй /cancel",
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, input_field_placeholder="Какое место?"),
                )
            )
            tg.create_task(redis.set(redis_key, new_meeting.model_dump_json(), ex=TEN_MINUTES))  # type: ignore[arg-type]

    return AddMeetingEnum.location


async def meeting_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    effective_chat, message, in_text, user = cast_defaults_command(update)
    new_location = Location(in_text)

    redis_key_new_meeting = get_redis_key(KeysEnum.new_meeting, chat_id=effective_chat.id)
    redis_key_meeting_list = get_redis_key(KeysEnum.meeting_list, chat_id=effective_chat.id)
    async with redis_connection() as redis:
        async with asyncio.TaskGroup() as tg:
            new_meeting_task = tg.create_task(redis.get(redis_key_new_meeting))  # type: ignore[arg-type]
            meetings_list_task = tg.create_task(get_meetings_list(redis, effective_chat.id))

        new_meeting_raw = new_meeting_task.result()
        meetings_list: MeetingList = meetings_list_task.result()

        new_meeting = Meeting.model_validate_json(new_meeting_raw)
        new_meeting.location = new_location
        try:
            meetings_list = add_meeting_in_meeting_list(meetings_list, new_meeting)
        except ValidationError as exc:
            await message.reply_text(str(exc))
        meetings_list.meetings[new_meeting.id] = new_meeting

        async with asyncio.TaskGroup() as tg:
            tg.create_task(redis.set(redis_key_meeting_list, meetings_list.model_dump_json()))  # type: ignore[arg-type]
            tg.create_task(
                message.reply_text(
                    f"Встреча запланирована {new_meeting.as_button()}" + "\nМожешь вернуться в меню /menu",
                )
            )

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    effective_chat, message, in_text, user = cast_defaults_command(update)
    await message.reply_text("Мое дело предложить - Ваше отказаться" " Будет скучно - пиши.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


ignore_commands_regex = "^(?!/)."
STATES = {
    AddMeetingEnum.title: [MessageHandler(filters.Regex(ignore_commands_regex), meeting_month)],
    AddMeetingEnum.month: [MessageHandler(filters.Regex(ignore_commands_regex), meeting_day)],
    AddMeetingEnum.day: [MessageHandler(filters.Regex(ignore_commands_regex), meeting_hour)],
    AddMeetingEnum.hour: [MessageHandler(filters.Regex(ignore_commands_regex), meeting_minute)],
    AddMeetingEnum.minute: [MessageHandler(filters.Regex(ignore_commands_regex), meeting_location)],
    AddMeetingEnum.location: [MessageHandler(filters.Regex(ignore_commands_regex), meeting_save)],
}

import asyncio
from uuid import UUID

from const import BASE_INLINE
from db import KeysEnum, get_redis_key
from extra_types import Callback, DetailedCallback
from handlers.const import CallbackEnum, DetailedCallbackEnum
from handlers.mappings import COMMON_CALLBACK_TO_DETAILED, DETAILED_CALLBACK_TEMPLATE
from handlers.meeting.utils import get_meeting, get_meetings_list
from models import Participant
from redis.asyncio import Redis
from telegram import Chat, InlineKeyboardButton, InlineKeyboardMarkup, Message, User


async def _do_meeting(
    chat: Chat,
    message: Message,
    raw_meeting_id: str,
    user: User,
    redis: Redis,
    is_leaving: bool,
) -> None:
    as_participant = Participant.from_user(user)
    meeting_id = UUID(raw_meeting_id)
    meetings_list = await get_meetings_list(redis, chat.id)
    meeting = meetings_list.meetings[meeting_id]

    if is_leaving:
        meeting.participants.remove(as_participant)
    else:
        meeting.participants.add(as_participant)

    special_message = "не участвует" if is_leaving else "участвует"
    redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat.id)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(redis.set(redis_key, meetings_list.model_dump_json()))  # type: ignore[arg-type]
        tg.create_task(
            message.edit_text(
                f"{as_participant!s} {special_message} в {meeting.as_button()}",
                reply_markup=InlineKeyboardMarkup(BASE_INLINE),
            )
        )


async def _do_meeting_chose(chat: Chat, message: Message, user: User, redis: Redis, callback_type: CallbackEnum) -> None:
    meeting_list = await get_meetings_list(redis, chat.id)
    as_participant = Participant.from_user(user)
    detailed_callback = COMMON_CALLBACK_TO_DETAILED[callback_type]
    is_leaving = callback_type == CallbackEnum.leave_meeting
    special_message = "не придешь" if is_leaving else "придешь"

    meetings_as_buttons = [
        [
            InlineKeyboardButton(
                text=meeting.as_button(),
                callback_data=DETAILED_CALLBACK_TEMPLATE[detailed_callback].substitute(meeting_id=meeting.id),
            )
        ]
        for meeting in meeting_list.meetings.values()
        if (as_participant not in meeting.participants and not is_leaving) or (as_participant in meeting.participants and is_leaving)
    ]
    meetings_as_buttons = [*BASE_INLINE, *meetings_as_buttons]
    keyboard = InlineKeyboardMarkup(inline_keyboard=meetings_as_buttons)
    await message.edit_text(f"Выбери куда {special_message}:", reply_markup=keyboard)


async def delete_meeting_chose(chat: Chat, message: Message, user: User, redis: Redis) -> None:
    meeting_list = await get_meetings_list(redis, chat.id)
    as_participant = Participant.from_user(user)

    meetings_as_buttons = [
        [
            InlineKeyboardButton(
                text=meeting.as_button(),
                callback_data=DETAILED_CALLBACK_TEMPLATE[DetailedCallbackEnum.delete_meeting_id].substitute(meeting_id=meeting.id),
            )
        ]
        for meeting in meeting_list.meetings.values()
        if hash(as_participant) == hash(meeting.initiator)
    ]
    meetings_as_buttons = [*BASE_INLINE, *meetings_as_buttons]
    keyboard = InlineKeyboardMarkup(inline_keyboard=meetings_as_buttons)
    await message.edit_text("Выбер какую встречу ты хочешь отменить:", reply_markup=keyboard)


async def participate_meeting_chose(chat: Chat, message: Message, user: User, redis: Redis) -> None:
    await _do_meeting_chose(chat=chat, message=message, user=user, redis=redis, callback_type=CallbackEnum.participate_meeting)


async def leave_meeting_chose(chat: Chat, message: Message, user: User, redis: Redis) -> None:
    await _do_meeting_chose(chat=chat, message=message, user=user, redis=redis, callback_type=CallbackEnum.leave_meeting)


async def participate_meeting(chat: Chat, message: Message, user: User, redis: Redis, meeting_id: str) -> None:
    await _do_meeting(
        chat=chat,
        message=message,
        raw_meeting_id=meeting_id,
        user=user,
        redis=redis,
        is_leaving=False,
    )


async def leave_meeting(chat: Chat, message: Message, user: User, redis: Redis, meeting_id: str) -> None:
    await _do_meeting(
        chat=chat,
        message=message,
        raw_meeting_id=meeting_id,
        user=user,
        redis=redis,
        is_leaving=True,
    )


async def retrieve_meeting(chat: Chat, message: Message, user: User, redis: Redis, meeting_id: str) -> None:
    meeting = await get_meeting(redis, chat.id, UUID(meeting_id))
    meetings_as_buttons = [*BASE_INLINE, [InlineKeyboardButton(text="Назад", callback_data=CallbackEnum.list_meetings)]]
    if meeting:
        text_out = meeting.as_detailed()
    else:
        text_out = "Мероприятие не найдено"
    keyboard = InlineKeyboardMarkup(inline_keyboard=meetings_as_buttons)
    await message.edit_text(text_out, reply_markup=keyboard)


async def delete_meeting(chat: Chat, message: Message, user: User, redis: Redis, meeting_id: str) -> None:
    meetings_list = await get_meetings_list(redis, chat.id)
    meetings_as_buttons = [*BASE_INLINE, [InlineKeyboardButton(text="Назад", callback_data=CallbackEnum.list_meetings)]]
    if meeting := meetings_list.meetings.get(UUID(meeting_id)):
        meetings_list.meetings.pop(meeting.id)
        text_out = f"Удалено:\n{meeting.as_detailed()}"
        redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat.id)
    else:
        text_out = "Мероприятие не найдено"

    keyboard = InlineKeyboardMarkup(inline_keyboard=meetings_as_buttons)
    async with asyncio.TaskGroup() as tg:
        tg.create_task(message.edit_text(text_out, reply_markup=keyboard))
        if meeting:
            tg.create_task(redis.set(redis_key, meetings_list.model_dump_json()))  # type: ignore[arg-type]


async def list_meetings(chat: Chat, message: Message, user: User, redis: Redis) -> None:
    redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat.id)
    meeting_list = await get_meetings_list(redis, chat.id)
    buttons = BASE_INLINE + [
        [
            InlineKeyboardButton(
                text=meeting.as_button(),
                callback_data=DETAILED_CALLBACK_TEMPLATE[DetailedCallbackEnum.retrieve_meeting_id].substitute(meeting_id=meeting.id),
            )
        ]
        for meeting in meeting_list.get_sorted_by_date_meetings()
    ]

    async with asyncio.TaskGroup() as tg:
        tg.create_task(redis.set(redis_key, meeting_list.model_dump_json()))  # type: ignore[arg-type]
        tg.create_task(message.edit_text("Список мероприятий", reply_markup=InlineKeyboardMarkup(buttons)))


async def add_meeting(chat: Chat, message: Message, user: User, redis: Redis) -> None:
    await message.edit_text(
        "Чтобы создать встречу нажми на команду /add_plan",
        reply_markup=InlineKeyboardMarkup(BASE_INLINE),
    )


DETAILED_CALLBACK_MAPPING: dict[DetailedCallbackEnum, DetailedCallback] = {
    DetailedCallbackEnum.participate_meeting_id: participate_meeting,
    DetailedCallbackEnum.leave_meeting_id: leave_meeting,
    DetailedCallbackEnum.retrieve_meeting_id: retrieve_meeting,
    DetailedCallbackEnum.delete_meeting_id: delete_meeting,
}

COMMON_CALLBACK_MAPPING: dict[CallbackEnum, Callback] = {
    CallbackEnum.participate_meeting: participate_meeting_chose,
    CallbackEnum.leave_meeting: leave_meeting_chose,
    CallbackEnum.list_meetings: list_meetings,
    CallbackEnum.add_meeting: add_meeting,
    CallbackEnum.delete_meeting: delete_meeting_chose,
}


__all__ = (
    "DETAILED_CALLBACK_MAPPING",
    "COMMON_CALLBACK_MAPPING",
)

import asyncio
from uuid import UUID

from const import BASE_INLINE
from db import KeysEnum, get_redis_key
from extra_types import MeetingCallback
from handlers.const import CallbackEnum
from models import MeetingList, Participant
from redis.asyncio import Redis
from telegram import Chat, InlineKeyboardMarkup, Message, User


async def get_meetings_list(redis: Redis, chat_id: int) -> MeetingList:
    redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat_id)
    meeting_list_raw = await redis.get(redis_key)
    meeting_list = MeetingList()  # type: ignore[call-arg]
    if meeting_list_raw:
        meeting_list = MeetingList.model_validate_json(meeting_list_raw)
        meeting_list = meeting_list.filter_outdated()
    return meeting_list


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


async def participate_meeting(chat: Chat, message: Message, meeting_id: str, user: User, redis: Redis) -> None:
    await _do_meeting(
        chat=chat,
        message=message,
        raw_meeting_id=meeting_id,
        user=user,
        redis=redis,
        is_leaving=False,
    )


async def leave_meeting(chat: Chat, message: Message, meeting_id: str, user: User, redis: Redis) -> None:
    await _do_meeting(
        chat=chat,
        message=message,
        raw_meeting_id=meeting_id,
        user=user,
        redis=redis,
        is_leaving=True,
    )


CALLBACK_MAPPING: dict[CallbackEnum, MeetingCallback] = {
    CallbackEnum.meeting_participate: participate_meeting,
    CallbackEnum.meeting_leave: leave_meeting,
}

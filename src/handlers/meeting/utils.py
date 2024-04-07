from db import KeysEnum, get_redis_key
from models import Meeting, MeetingList
from pydantic import ValidationError
from redis.asyncio import Redis


async def get_meetings_list(redis: Redis, chat_id: int) -> MeetingList:
    redis_key = get_redis_key(key=KeysEnum.meeting_list, chat_id=chat_id)
    meeting_list_raw = await redis.get(redis_key)
    meeting_list = MeetingList()  # type: ignore[call-arg]
    if meeting_list_raw:
        meeting_list = MeetingList.model_validate_json(meeting_list_raw)
        meeting_list = meeting_list.filter_outdated()
    return meeting_list


def add_meeting_in_meeting_list(meetings_list: MeetingList, new_meeting: Meeting) -> MeetingList:
    if meetings_list.check_new_meeting_in_list(new_meeting):
        raise ValidationError(f"Такая встреча уже запланирована: \n{new_meeting}")
    meetings_list.meetings.update({new_meeting.id: new_meeting})
    return meetings_list

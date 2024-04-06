from datetime import datetime
from typing import Annotated, Any

from extra_types import AutoUUID, LocationId, Participants
from pydantic import BaseModel, Field, field_serializer


class Meeting(BaseModel):
    id: AutoUUID
    date: datetime
    title: str
    location: Annotated[LocationId | None, Field(default=None, description="Место встречи")]
    participants: Participants


class ChatGroup(BaseModel):
    chat_id: int
    is_logged: Annotated[bool, Field(default=False, description="Флаг авторизации")]

    @field_serializer("is_logged")
    def serialize_dt(self, v: bool, _info: Any) -> int:
        return int(v)

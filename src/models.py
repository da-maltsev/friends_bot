import hashlib
from datetime import datetime
from typing import Annotated, Self

from config import settings
from extra_types import AutoUUID, Location, Participants
from pydantic import BaseModel, Field, field_serializer
from telegram import User
from utils import safe_str


class Participant(BaseModel):
    first_name: Annotated[str, Field(description="Имя", serialization_alias="Имя")]
    last_name: Annotated[str, Field(description="Фамилия", serialization_alias="Фамилия")]
    username: Annotated[str, Field(description="Логин", serialization_alias="Логин")]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} (@{self.username})"

    def as_button(self) -> str:
        return f"@{self.username}"

    def __hash__(self) -> int:
        hash_string = f"{self.first_name}{self.last_name}{self.username}"
        return int(hashlib.md5(hash_string.encode()).hexdigest(), 16)

    @classmethod
    def from_user(cls, user: User) -> "Participant":
        return cls(
            first_name=safe_str(user, "first_name"),
            last_name=safe_str(user, "last_name"),
            username=safe_str(user, "username"),
        )


class Meeting(BaseModel):
    id: AutoUUID
    participants: Participants
    date: Annotated[datetime, Field(description="Дата встречи", serialization_alias="Дата встречи")]
    title: Annotated[str, Field(description="Название встречи", serialization_alias="Название встречи")]
    location: Annotated[Location | None, Field(default=None, description="Место встречи", serialization_alias="место")]
    initiator: Participant

    @field_serializer("id")
    def serialize_id(self, value: AutoUUID) -> str:
        return str(value)

    def as_button(self) -> str:
        location = self.location if self.location else "?"
        return f"{self.title.capitalize()} - {datetime.strftime(self.date, "%d-%m, %H:%M")} - {location} "

    def as_detailed(self) -> str:
        location = self.location if self.location else "Место не указано"
        participants = "\n".join(str(participant) for participant in self.participants)
        return f"""
          {self.title.capitalize()}
          Дата: {datetime.strftime(self.date, "%d-%m, %H:%M")}
          Место: {location}
          Предложил: {self.initiator}
          Участники: {participants}
        """

    def __hash__(self) -> int:
        hash_string = f"{self.location}{self.date}{self.title}"
        return int(hashlib.md5(hash_string.encode()).hexdigest(), 16)


class MeetingList(BaseModel):
    meetings: Annotated[
        dict[AutoUUID, Meeting],
        Field(
            default_factory=dict,
            description="Список встреч",
            serialization_alias="Список встреч",
        ),
    ]

    def filter_outdated(self) -> Self:
        filtered_meetings = {id: elem for id, elem in self.meetings.items() if elem.date > datetime.now(tz=settings.tz_info)}
        self.meetings = filtered_meetings
        return self

    def get_sorted_by_date_meetings(self) -> list[Meeting]:
        return sorted(self.meetings.values(), key=lambda x: x.date)

    def check_new_meeting_in_list(self, meeting: Meeting) -> bool:
        return hash(meeting) in {hash(meeting) for meeting in self.meetings.values()}

    def __str__(self) -> str:
        return "Список встреч:" + "\n".join(str(meeting) for meeting in sorted(self.meetings.values(), key=lambda x: x.date))


class ChatGroup(BaseModel):
    chat_id: int
    is_logged: Annotated[bool, Field(default=False, description="Флаг авторизации")]

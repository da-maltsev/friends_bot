from collections.abc import Callable, Coroutine
from typing import TYPE_CHECKING, Annotated, NewType
from uuid import UUID, uuid4

from pydantic import Field
from redis.asyncio import Redis
from telegram import Chat, Message, User

if TYPE_CHECKING:
    from models import Participant

MessageText = NewType("MessageText", str)
Location = NewType("Location", str)
AutoUUID = Annotated[UUID, Field(default_factory=uuid4)]
Participants = Annotated[
    set["Participant"],
    Field(
        default_factory=set,
        description="Участники",
        serialization_alias="Участники",
    ),
]
Callback = Callable[[Chat, Message, User, Redis], Coroutine]
DetailedCallback = Callable[[Chat, Message, User, Redis, str], Coroutine]

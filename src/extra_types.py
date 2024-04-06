from typing import TYPE_CHECKING, Annotated, NewType
from uuid import UUID, uuid4

from pydantic import Field

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

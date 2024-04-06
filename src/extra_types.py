from typing import Annotated, NewType
from uuid import UUID, uuid4

from pydantic import Field

MessageText = NewType("MessageText", str)
Participant = NewType("Participant", str)
LocationId = NewType("LocationId", str)
AutoUUID = Annotated[UUID, Field(default_factory=uuid4)]
Participants = Annotated[set[Participant], Field(default_factory=set, description="Участники")]

from enum import Enum
from string import Template


class CallbackEnum(str, Enum):
    meeting_participate = "meeting-participate"
    meeting_leave = "meeting-leave"


CALLBACK_TEMPLATE: dict[CallbackEnum, Template] = {
    CallbackEnum.meeting_participate: Template(CallbackEnum.meeting_participate + "|${meeting_id}"),
    CallbackEnum.meeting_leave: Template(CallbackEnum.meeting_leave + "|${meeting_id}"),
}


def parse_callback(callback: str) -> tuple[CallbackEnum, str]:
    callback_type, callback_id = callback.split("|")
    return CallbackEnum(callback_type), callback_id

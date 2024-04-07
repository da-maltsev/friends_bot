from string import Template

from extra_types import Callback, DetailedCallback
from handlers.const import CallbackEnum, DetailedCallbackEnum

DETAILED_CALLBACK_TEMPLATE: dict[DetailedCallbackEnum, Template] = {
    DetailedCallbackEnum.participate_meeting_id: Template(DetailedCallbackEnum.participate_meeting_id + "|${meeting_id}"),
    DetailedCallbackEnum.leave_meeting_id: Template(DetailedCallbackEnum.leave_meeting_id + "|${meeting_id}"),
}

COMMON_CALLBACK_TO_DETAILED: dict[CallbackEnum, DetailedCallbackEnum] = {
    CallbackEnum.participate_meeting: DetailedCallbackEnum.participate_meeting_id,
    CallbackEnum.leave_meeting: DetailedCallbackEnum.leave_meeting_id,
}


def get_detailed_callback(callback_type: DetailedCallbackEnum) -> DetailedCallback:
    from handlers.meeting import DETAILED_CALLBACK_MAPPING as MEETING_DETAILED_CALLBACK_MAPPING

    detailed_mapping: dict[DetailedCallbackEnum, DetailedCallback] = {**MEETING_DETAILED_CALLBACK_MAPPING}
    return detailed_mapping[callback_type]


def get_common_callback(callback_type: CallbackEnum) -> Callback:
    from handlers.meeting import COMMON_CALLBACK_MAPPING as MEETING_COMMON_CALLBACK_MAPPING

    common_mapping: dict[CallbackEnum, Callback] = {**MEETING_COMMON_CALLBACK_MAPPING}
    return common_mapping[callback_type]

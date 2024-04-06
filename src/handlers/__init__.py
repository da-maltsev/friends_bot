from handlers.meeting import AddMeetingCommand, ListMeetingCommand, ParticipateMeetingCommand
from handlers.start import help, start
from telegram.ext import CommandHandler

registry = [
    CommandHandler("start", start),
    CommandHandler("help", help),
    CommandHandler("plan_list", ListMeetingCommand.run),
    CommandHandler("plan_add", AddMeetingCommand.run),
    CommandHandler("plan_part", ParticipateMeetingCommand.run),
]


__all__ = [
    "registry",
]

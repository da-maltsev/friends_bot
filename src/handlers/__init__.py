from handlers.meeting import AddMeetingCommand, LeaveMeetingCommand, ListMeetingCommand, ParticipateMeetingCommand
from handlers.start import help, start
from telegram.ext import CommandHandler

registry = [
    CommandHandler("start", start),
    CommandHandler("help", help),
    CommandHandler(ListMeetingCommand.COMMAND, ListMeetingCommand.run),
    CommandHandler(AddMeetingCommand.COMMAND, AddMeetingCommand.run),
    CommandHandler(ParticipateMeetingCommand.COMMAND, ParticipateMeetingCommand.run),
    CommandHandler(LeaveMeetingCommand.COMMAND, LeaveMeetingCommand.run),
]


__all__ = [
    "registry",
]

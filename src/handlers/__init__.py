from handlers.callbacks import keyboard_callback
from handlers.meeting import AddMeetingCommand, LeaveMeetingCommand, ListMeetingCommand, ParticipateMeetingCommand
from handlers.start import help, start
from telegram.ext import CallbackQueryHandler, CommandHandler

commands = [
    CommandHandler("start", start),
    CommandHandler("help", help),
    CommandHandler(ListMeetingCommand.COMMAND, ListMeetingCommand.run),
    CommandHandler(AddMeetingCommand.COMMAND, AddMeetingCommand.run),
    CommandHandler(ParticipateMeetingCommand.COMMAND, ParticipateMeetingCommand.run),
    CommandHandler(LeaveMeetingCommand.COMMAND, LeaveMeetingCommand.run),
]
callbacks = [
    CallbackQueryHandler(keyboard_callback),
]
registry = commands + callbacks


__all__ = [
    "registry",
    "commands",
]

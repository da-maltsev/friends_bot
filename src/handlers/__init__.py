from handlers.callbacks import keyboard_callback
from handlers.meeting.conversation import STATES, add_meeting, cancel
from handlers.start import help, menu, start
from telegram.ext import CallbackQueryHandler, CommandHandler, ConversationHandler

commands = [
    CommandHandler("start", start),
    CommandHandler("help", help),
    CommandHandler("menu", menu),
]
callbacks = [
    CallbackQueryHandler(keyboard_callback),
]
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("add_plan", add_meeting)],
    states=STATES,  # type: ignore[arg-type]
    fallbacks=[CommandHandler("cancel", cancel)],
)
registry = [conv_handler, *commands, *callbacks]


__all__ = [
    "registry",
    "commands",
]

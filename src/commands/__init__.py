from commands.start import start
from telegram.ext import CommandHandler

registry = (CommandHandler("start", start),)

__all__ = ["registry"]

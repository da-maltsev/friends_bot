from typing import cast

from extra_types import MessageText
from telegram import Chat, Message, Update


def cast_defaults(update: Update) -> tuple[Chat, Message, MessageText]:
    effective_chat = cast("Chat", update.effective_chat)
    message = cast("Message", update.message)
    in_text = cast(MessageText, message.text)
    return effective_chat, message, in_text

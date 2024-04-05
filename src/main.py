import logging

import commands
from config import settings
from telegram.ext import ApplicationBuilder

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO if settings.DEBUG else logging.WARNING,
)


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.TG_TOKEN).build()

    for command_handler in commands.registry:
        application.add_handler(command_handler)

    application.run_polling()

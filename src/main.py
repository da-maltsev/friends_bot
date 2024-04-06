import logging

import handlers
from config import settings
from telegram.ext import ApplicationBuilder

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO if settings.DEBUG else logging.WARNING,
)


if __name__ == "__main__":
    application = ApplicationBuilder().token(settings.TG_TOKEN).build()

    for handler in handlers.registry:
        application.add_handler(handler)

    application.run_polling()

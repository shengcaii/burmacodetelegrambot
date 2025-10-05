from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from src.bot.handlers import start, handle_text, handle_photo, unknown_command, debug_all, error_handler
from src.config import BOT_TOKEN

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN is not set in the environment.")

application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

application.add_handler(CommandHandler("start", start))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
application.add_handler(MessageHandler(filters.ALL, debug_all))
application.add_error_handler(error_handler)
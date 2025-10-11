from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from src.bot.handlers import start, help_command,check_alive, handle_text,unknown_command, error_handler, search_web, remove_background
from src.config import BOT_TOKEN

if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN is not set in the environment.")

application = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .build()
)

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("isalive", check_alive))
application.add_handler(CommandHandler("search", search_web))
application.add_handler(CommandHandler("removebg", remove_background))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
application.add_error_handler(error_handler)
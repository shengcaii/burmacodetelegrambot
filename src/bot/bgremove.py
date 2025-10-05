import os
from dotenv import load_dotenv
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
API_KEY = os.getenv("API_KEY")  # Placeholder for your remove.bg API key
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Placeholder for your Telegram Bot Token
WELCOME_TEXT = "Welcome to the Background Remover Bot! Send me a photo and I'll remove its background."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text(WELCOME_TEXT)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.photo:
        if update.message:
            await update.message.reply_text("No photo found in the message.")
        return
    photo_file = await update.message.photo[-1].get_file()
    file_path = "input.jpg"
    await photo_file.download_to_drive(file_path)

    with open(file_path, "rb") as image_file:
        response = requests.post(
            "https://api.remove.bg/v1.0/removebg",
            files={"image_file": image_file},
            data={"size": "auto"},
            headers={"X-Api-Key": API_KEY}
        )
    if response.status_code == requests.codes.ok:
        output_path = "no-bg.png"
        with open(output_path, "wb") as out:
            out.write(response.content)
        await update.message.reply_photo(photo=open(output_path, "rb"))
    else:
        await update.message.reply_text("Error removing background: " + response.text)

def main():
    if not API_KEY or not BOT_TOKEN:
        print("Error: API_KEY and BOT_TOKEN must be set in environment variables.")
        return
    app = ApplicationBuilder().pool_timeout(120).read_timeout(120).token(BOT_TOKEN).build()
    print("Bot started...")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
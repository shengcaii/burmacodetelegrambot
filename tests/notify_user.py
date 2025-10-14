import os
import requests
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_ID = os.getenv("TELEGRAM_USER_ID") # Set this in your .env file for the user you want to notify

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in the environment.")
if not USER_ID:
    raise ValueError("TELEGRAM_USER_ID is not set in the environment. Please set the user ID you want to notify.")

def send_telegram_message(user_id: str, message: str):
    """Sends a message to a specific Telegram user via the bot."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": user_id,
        "text": message,
        "parse_mode": "HTML" # You can change this to MarkdownV2 or None
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Message sent successfully to user {user_id}.")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to user {user_id}: {e}")
        return None

if __name__ == "__main__":
    test_message = "<b>Test Notification:</b> This is <a>a test message</a> from your Telegram bot."
    send_telegram_message(USER_ID, test_message)

    # Example of sending a reminder
    # reminder_message = "<b>Reminder:</b> Don't forget your meeting at 3 PM!"
    # send_telegram_message(USER_ID, reminder_message)

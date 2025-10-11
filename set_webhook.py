import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Should be your public base URL, e.g., https://your-public-url

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("BOT_TOKEN or WEBHOOK_URL not set in .env")

set_webhook_url = f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook"
get_webhook_info_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo"

# response = requests.get(set_webhook_url, params={"url": WEBHOOK_URL})
# print(response.json())

print(f"Webhook set to: {WEBHOOK_URL}")
info_response = requests.get(get_webhook_info_url)
print("Current webhook info:", info_response.json())
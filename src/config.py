from dotenv import load_dotenv
import os
from bot.utils import get_model_list

# Load variables from .env file
load_dotenv()

# Access environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_ENDPOINT = os.getenv("OPENROUTER_API_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
# Validate and parse the model list
MODEL_LIST = get_model_list(os.getenv("LLM_MODELS"))
# Add more as needed

REQUIRED_VARS = {
    "BOT_TOKEN": BOT_TOKEN,
    "WEBHOOK_URL": WEBHOOK_URL,
    "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
}

for var_name, var_value in REQUIRED_VARS.items():
    if not var_value:
        raise ValueError(f"Required environment variable '{var_name}' is not set.")
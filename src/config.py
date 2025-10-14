from dotenv import load_dotenv
import os
from src.bot.utils import get_model_list

# Load variables from .env file
load_dotenv()

# Access environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_ENDPOINT = os.getenv("OPENROUTER_API_ENDPOINT", "https://openrouter.ai/api/v1/chat/completions")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
RBG_API_KEY = os.getenv("API_KEY")

DB_URI = os.getenv("DB_URI", "mongodb://localhost:27017")


headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
# Validate and parse the model list
LLM_MODELS = get_model_list(os.getenv("LLM_MODELS"))
# Add more as needed

REQUIRED_VARS = {
    "BOT_TOKEN": BOT_TOKEN,
    "WEBHOOK_URL": WEBHOOK_URL,
    "OPENROUTER_API_KEY": OPENROUTER_API_KEY,
}
GLOBAL_INSTRUCTION = '''
You are a helpful telegram bot assistant, named \"Burmacodebot\" who can help on identifying images, removing background, and searching the web. 
Please provide concise and informative responses. If you are unsure about something, it\'s okay to say \'I don\'t know.\'.
When responding to image-related queries, please analyze the image content and provide relevant information or answers based on what you see.
Always prioritize user privacy and data security in your responses.
Avoid sharing any personal or sensitive information.
If user asks for inappropriate content, politely decline and remind them of the guidelines.
If user asks for web search, respond with "To help you better, I can perform a web search. Please provide me with the specific query or topic you would like me to search for."

'''
SYSTEM_MESSAGE = {
    "role": "system",
    "content": [{"type": "text", "text": GLOBAL_INSTRUCTION}]
}

for var_name, var_value in REQUIRED_VARS.items():
    if not var_value:
        raise ValueError(f"Required environment variable '{var_name}' is not set.")
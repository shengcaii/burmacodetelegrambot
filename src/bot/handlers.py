import httpx
from telegram import Update
from telegram.ext import ContextTypes
from config import OPENROUTER_API_KEY, OPENROUTER_API_ENDPOINT, headers
from bot.utils import encode_bytes_to_base64

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Received /start command")
    if update.message:
        first_name = update.effective_user.first_name if update.effective_user else ""
        await update.message.reply_text(f"Hello {first_name}! Send me an image and I'll tell you what's in it!".replace(" !", ""))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_history = context.user_data.setdefault("history", []) if context.user_data is not None else []
    if not update.message or not update.message.text:
        if update.message:
            await update.message.reply_text("No text found in the message.")
        return
    
    await update.message.reply_text("Let me think...")

    user_history.append({
        "role": "user",
        "content": [{"type": "text", "text": update.message.text}]
    })

    # Use the imported headers directly
    payload = {
        "model": "deepseek/deepseek-chat-v3.1:free",
        "messages": user_history
    }
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]

        user_history.append({
            "role": "assistant",
            "content": [{"type": "text", "text": result}]
        })
        await update.message.reply_text(result)
    except httpx.HTTPStatusError as e:
        #TODO: change error message to be more user-friendly and logs the error details somewhere
        await update.message.reply_text(f"API Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_history = context.user_data.setdefault("history", []) if context.user_data is not None else []
    if not update.message or not update.message.photo:
        if update.message:
            await update.message.reply_text("No photo found in the message.")
        return

    await update.message.reply_text("Identifying your image, please wait...")

    # 1. Download image directly into memory to avoid disk I/O
    photo_file = await update.message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()

    # 2. Encode the in-memory image using the utility function
    base64_image = encode_bytes_to_base64(image_bytes)
    data_url = f"data:image/jpeg;base64,{base64_image}"

    user_history.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "What's in this image? Describe only in brief."
                },
                {
                    "type": "image_url", "image_url": {"url": data_url}
                }
            ]
        }
    )

    payload = {
        # 3. Use a vision-capable model.
        # You could enhance this to filter your MODEL_LIST for vision models.
        "model": "mistralai/mistral-small-3.2-24b-instruct:free",
        "messages": user_history
    }

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(OPENROUTER_API_ENDPOINT, headers=headers, json=payload, timeout=60)
            # 4. Add proper error handling for bad API responses
            response.raise_for_status()
            
            response_data = response.json()
            result = response_data["choices"][0]["message"]["content"]

        user_history.append({
            "role": "assistant",
            "content": [{"type": "text", "text": result}]
        })
        await update.message.reply_text(result)
    except httpx.HTTPStatusError as e:
        #TODO: change error message to be more user-friendly and logs the error details somewhere
        await update.message.reply_text(f"API Error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Unknown command.")


async def debug_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("Debug handler triggered:", update)

async def error_handler(update, context):
    print("Trigger error handler")
    print(f"Error: {context.error}")
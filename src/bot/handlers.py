import httpx
import logging
import io
import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from src.config import OPENROUTER_API_ENDPOINT, headers, LLM_MODELS, RBG_API_KEY, SYSTEM_MESSAGE
from src.database.user_db import update_or_create_user
from src.database.chat_history_db import get_user_history, add_message_to_history
from src.bot.utils import encode_bytes_to_base64, try_models

# Set up basic logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.ERROR
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if update.message and user:
        # Run the synchronous database call in a separate thread
        await asyncio.to_thread(update_or_create_user, user)

        first_name = user.first_name
        await update.message.reply_text(
            f"Hello {first_name}! Thanks for reaching out. How can I assist you today?"
            "\n\nYou can type /help to see what I can do!"
            )

async def check_alive(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("Yes, I'm alive and ready to assist you! 🤖")    

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        help_text = (
            "Here are some commands you can use:\n"
            "/start - Start the bot and get a welcome message.\n"
            "/isalive? - Check if the bot is running.\n"
            "/search <query> - Search the web for information.\n"
            "/removebg - Remove the background from an image (send as caption or reply to an image).\n\n"
            "You can also send me any text message, and I'll do my best to assist you! 🤖\n"
            "/help - Show this help message again.\n"
        )
        await update.message.reply_text(help_text)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # The MessageHandler with filters.TEXT ensures message and message.text exist.
    user = update.effective_user
    message = update.effective_message
    if not user or not message or not message.text:
        return # Should not happen with correct filters, but good for safety

    # Send a placeholder message that we can edit later
    thinking_message = await message.reply_text("Thinking...")

    # 1. Fetch recent history from the database
    user_history = await asyncio.to_thread(get_user_history, user.id)

    # 2. Add system message and current user message
    # Prepending the system message ensures the LLM follows instructions
    user_history.insert(0, SYSTEM_MESSAGE)
    user_history.append({"role": "user", "content": message.text})

    # 3. Save the user's new message to the database in the background ("fire-and-forget").
    # This allows us to call the LLM immediately without waiting for the database write.
    asyncio.create_task(asyncio.to_thread(add_message_to_history, user.id, "user", message.text))

    payload = {"messages": user_history}

    # Call the decoupled try_models function
    result = await try_models(
        models=LLM_MODELS,
        payload_base=payload,
        headers=headers,
        endpoint=OPENROUTER_API_ENDPOINT,
    )

    if result:
        # The assistant's response is no longer saved to the database.
        await thinking_message.edit_text(result)
    else:
        # If all models failed, inform the user by editing the placeholder message.
        await thinking_message.edit_text(
            "I'm having trouble connecting to my brain right now. Please try again later."
        )

async def identify_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        logger.error(f"API Error during image identification: {e.response.status_code} - {e.response.text}")
        await update.message.reply_text("Sorry, I'm having trouble understanding images right now. Please try again later.")
    except Exception as e:
        logger.error(f"Unexpected error during image identification: {e}", exc_info=True)
        await update.message.reply_text("An unexpected error occurred while processing your image. Please try again.")

async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message:
        await update.message.reply_text("This command is not supported yet :( ")

async def search_web(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_history = context.user_data.setdefault("history", []) if context.user_data is not None else []
    if not update.message or not context.args:
        if update.message:
            await update.message.reply_text("Please provide a search query after /search. For example: /search What is the capital of France?")
        return

    await update.message.reply_text("Searching the web, please wait...")
    print(context.args)
    search_query = " ".join(context.args)

    user_history.append({
        "role": "user",
        "content": [{"type": "text", "text": search_query}]
    })

    payload = {
        "plugins": [{ "id": "web" }],
        "messages": user_history
    }
    result = await try_models(
        models=LLM_MODELS,
        headers=headers,
        payload_base=payload,
        endpoint=OPENROUTER_API_ENDPOINT
    )
    if result:
        user_history.append({
            "role": "assistant",
            "content": [{"type": "text", "text": result}]
        })
        await update.message.reply_text(result)
    else:
        await update.message.reply_text("No results found.")

async def remove_background(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    if not message:
        return

    if not RBG_API_KEY:
        await message.reply_text("The background removal feature is not configured. Please contact the bot administrator.")
        return

    # Determine which message contains the photo
    photo_message = message
    if message.reply_to_message and message.reply_to_message.photo:
        photo_message = message.reply_to_message

    if not photo_message or not photo_message.photo:
        await message.reply_text("Please send this command as a caption to a photo, or reply to a photo with this command.")
        return

    await message.reply_text("Removing background, please wait...")
    photo_file = await photo_message.photo[-1].get_file()
    image_bytes = await photo_file.download_as_bytearray()
    image_stream = io.BytesIO(image_bytes)

    try:
        async with httpx.AsyncClient(timeout=60) as client:
                response = await client.post(
                        "https://api.remove.bg/v1.0/removebg",
                        headers={"X-Api-Key": RBG_API_KEY},
                        files={"image_file": ("image.jpg", image_stream, "image/jpeg")},
                        data={"size": "auto"}
                    )
                response.raise_for_status() # Raise an exception for bad status codes
                
                # Send the image directly from memory without saving to a file
                processed_image_stream = io.BytesIO(response.content)
                await message.reply_photo(photo=processed_image_stream)
    except httpx.HTTPStatusError as e:
        logger.error(f"Background removal API Error: {e.response.status_code} - {e.response.text}")
        await message.reply_text("Sorry, I couldn't remove the background from the image. Please try again later.")
    except Exception as e:
        logger.error(f"Unexpected error during background removal: {e}", exc_info=True)
        await message.reply_text("An unexpected error occurred while removing the background. Please try again.")

async def debug_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug("Debug handler triggered: %s", update)

async def error_handler(update, context):
    logger.error("Exception while handling an update:", exc_info=context.error)
    
    if update and update.effective_message:
        first_name = update.effective_user.first_name if update.effective_user else "there"
        await update.effective_message.reply_text(f"Hi {first_name}, it looks like something went wrong on our side. Please try again later!")
import logging
from datetime import datetime, timezone
from .db import get_db_client

logger = logging.getLogger(__name__)

def add_message_to_history(user_id: int, role: str, content: str):
    """
    Adds a single message (from user or assistant) to the user's chat history.
    """
    try:
        client = get_db_client()
        db = client.get_database("telegram_bot_db")
        history_collection = db.get_collection("chat_history")

        message_document = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "timestamp": datetime.now(timezone.utc)
        }
        history_collection.insert_one(message_document)
    except Exception as e:
        logger.error(f"Database error when adding chat history for user {user_id}: {e}", exc_info=True)

def get_user_history(user_id: int, limit: int = 10):
    """
    Retrieves the most recent messages for a user.
    Returns a list of message dictionaries, oldest first.
    """
    try:
        client = get_db_client()
        db = client.get_database("telegram_bot_db")
        history_collection = db.get_collection("chat_history")

        # Find messages for the user, sort by timestamp descending, and limit results
        messages_cursor = history_collection.find(
            {"user_id": user_id}
        ).sort("timestamp", -1).limit(limit)

        # The messages are newest-first, so we reverse them to get chronological order
        messages = list(messages_cursor)
        return [{"role": msg["role"], "content": msg["content"]} for msg in reversed(messages)]

    except Exception as e:
        logger.error(f"Database error when retrieving chat history for user {user_id}: {e}", exc_info=True)
        return []
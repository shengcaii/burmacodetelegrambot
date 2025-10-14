import logging
from datetime import datetime, timezone
from telegram import User
from .db import get_db_client
 
logger = logging.getLogger(__name__)

def update_or_create_user(user: User):
    """
    Saves or updates a user's information in the database.
    Uses user.id as the unique identifier.
    """
    if not user:
        return

    try:
        client = get_db_client()
        db = client.get_database("telegram_bot_db") # Standardize database name
        users_collection = db.get_collection("users")

        # Data to be saved or updated
        user_data = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "language_code": user.language_code,
            "last_seen": datetime.now(timezone.utc)
        }

        # Use update_one with upsert=True to create or update the user
        users_collection.update_one({"_id": user.id}, {"$set": user_data}, upsert=True)
    except Exception as e:
        logger.error(f"Database error when updating user {user.id}: {e}", exc_info=True)
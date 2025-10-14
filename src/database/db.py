from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from src.config import DB_URI
import pymongo

# Create a single, global client instance.
# This is thread-safe and manages a connection pool internally.
_client = MongoClient(DB_URI, server_api=ServerApi('1'))

def get_db_client():
    """
    Returns the shared MongoDB client instance.
    """
    return _client

def ensure_indexes():
    """
    Ensures that the necessary indexes are created in the database.
    This function is idempotent and can be safely called on application startup.
    """
    try:
        client = get_db_client()
        db = client.get_database("telegram_bot_db")
        
        # Create a compound index on the chat_history collection.
        # This optimizes queries that filter by user_id and sort by timestamp.
        chat_history_collection = db.get_collection("chat_history")
        chat_history_collection.create_index([
            ("user_id", pymongo.ASCENDING),
            ("timestamp", pymongo.DESCENDING)
        ])
        print("Database indexes ensured for chat_history collection.")
    except Exception as e:
        print(f"An error occurred while ensuring database indexes: {e}")

# This block will only run when the script is executed directly
# e.g., `python -m src.database.db`
if __name__ == "__main__":
    try:
        client = get_db_client()
        client.admin.command('ping')
        print("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
import asyncio
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

# Set your deployed Render webhook URL here
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "https://your-render-app.onrender.com/webhook")
print(WEBHOOK_URL)
counter = 0
failed = 0
async def send_test_update(session, i):
    # Minimal Telegram update payload (simulate /start command)
    global counter, failed
    counter +=1
    payload = {
        "update_id": 1000000 + i,
        "message": {
            "message_id": i,
            "from": {"id": 123456, "is_bot": False, "first_name": "Test"},
            "chat": {"id": 123456, "first_name": "Test", "type": "private"},
            "date": 1759642301,
            "text": "hi",
            "entities": [{"offset": 0, "length": 6, "type": "bot_command"}]
        }
    }
    try:
        resp = await session.post(WEBHOOK_URL, json=payload, timeout=15)
        print(f"Request {i}: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Request {i} failed: {e}")
        failed +=1

async def main():
    num_requests = int(os.getenv("NUM_REQUESTS", 50))  # Number of concurrent requests
    async with httpx.AsyncClient() as session:
        tasks = [send_test_update(session, i) for i in range(num_requests)]
        await asyncio.gather(*tasks)
    print(counter, failed)
if __name__ == "__main__":
    asyncio.run(main())

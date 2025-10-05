from telegram import Update
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from .bot.application import application  # Import your PTB Application

app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await application.initialize()
    await application.start()
    yield
    await application.stop()
    await application.shutdown()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def check_health():
    return {"message": "Telegram Bot is running!"}


@app.post("/webhook")
async def telegram_webhook(request: Request):
    update_dict = await request.json()
    update = Update.de_json(update_dict, application.bot)
    await application.process_update(update)
    return {"ok": True}
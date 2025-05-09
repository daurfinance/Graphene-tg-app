from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import logging
from dotenv import load_dotenv
import os
import gettext

# Load environment variables
load_dotenv()

# Telegram Bot Setup
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in the .env file")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Initialize gettext for multilingual support
locales_dir = 'locales'
language = 'en'
gettext.bindtextdomain('graphene_bot', locales_dir)
gettext.textdomain('graphene_bot')
_ = gettext.gettext

# FastAPI Setup
app = FastAPI()

# Add CORS middleware for better API compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Improved logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GrapheneBot")
logger.info("Bot and API are starting...")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Graphene Telegram Bot Web Interface!"}

# Telegram Webhook Setup
WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"https://<your-vercel-domain>{WEBHOOK_PATH}"

@app.post(WEBHOOK_PATH)
async def telegram_webhook(request: Request):
    update = await request.json()
    await dp.process_update(update)
    return {"ok": True}

# Set webhook on startup
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)

# Remove webhook on shutdown
@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()

# Telegram Bot Handlers
@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    await message.reply(_("Welcome to the Graphene Bot! Use /help to see available commands."))

@dp.message_handler(commands=['help'])
async def send_help(message: Message):
    await message.reply(_("Available commands: /start, /help, /buy, /airdrop, /stake"))

# Run the bot in the background
import asyncio
from threading import Thread

def start_bot():
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

Thread(target=start_bot).start()

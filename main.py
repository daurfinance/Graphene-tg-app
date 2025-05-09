from fastapi import FastAPI
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.contrib.middlewares.logging import LoggingMiddleware
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
dp.middleware.setup(LoggingMiddleware())

# Initialize gettext for multilingual support
locales_dir = 'locales'
language = 'en'
gettext.bindtextdomain('graphene_bot', locales_dir)
gettext.textdomain('graphene_bot')
_ = gettext.gettext

# FastAPI Setup
app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Graphene Telegram Bot Web Interface!"}

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

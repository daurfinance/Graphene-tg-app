from flask import Flask, request, jsonify
from aiogram import Bot, Dispatcher
from aiogram.types import Message
import logging
from dotenv import load_dotenv
import os
import gettext
import asyncio
from threading import Thread

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

# Функция для выбора языка в зависимости от предпочтений пользователя
def get_user_language(user_id):
    # Здесь можно добавить логику получения языка из базы данных
    # Пока просто возвращаем русский для тестирования
    return 'ru'

# Функция для динамического переключения языка
def localize(text, lang='en'):
    # Устанавливаем язык и возвращаем перевод
    try:
        translation = gettext.translation('graphene_bot', locales_dir, languages=[lang])
        translation.install()
        return translation.gettext(text)
    except FileNotFoundError:
        # Если перевод не найден, используем English
        return text

# Flask Setup
app = Flask(__name__)

# Improved logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GrapheneBot")
logger.info("Bot and API are starting...")

@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"message": "Welcome to the Graphene Telegram Bot Web Interface!"})

# Telegram Webhook Setup
WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"
WEBHOOK_URL = os.getenv("VERCEL_URL", "https://graphene-tg-app.vercel.app") + WEBHOOK_PATH

@app.route(WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    asyncio.run(dp.process_update(update))
    return jsonify({"ok": True})

@app.route("/buy", methods=["GET"])
def buy_page():
    return jsonify({"message": "Страница покупки токенов находится в разработке."})

@app.route("/airdrop", methods=["GET"])
def airdrop_page():
    return jsonify({"message": "Страница участия в эйрдропе находится в разработке."})

@app.route("/stake", methods=["GET"])
def stake_page():
    return jsonify({"message": "Страница стейкинга находится в разработке."})

# Set webhook on startup
with app.app_context():
    @app.before_request
    def on_startup():
        # Исправленная функция для установки webhook при первом запросе
        if not hasattr(app, "_webhook_set"):
            asyncio.run(bot.set_webhook(WEBHOOK_URL))
            app._webhook_set = True

# Remove webhook on shutdown
@app.teardown_appcontext
def on_shutdown(exception):
    asyncio.run(bot.delete_webhook())

# Telegram Bot Handlers
@dp.message_handler(commands=['start'])
async def send_welcome(message: Message):
    await message.reply(_("Welcome to the Graphene Bot! Use /help to see available commands."))

@dp.message_handler(commands=['help'])
async def send_help(message: Message):
    await message.reply(_("Available commands: /start, /help, /buy, /airdrop, /stake"))

# Run the flask server
if __name__ == "__main__":
    # В режиме разработки используем polling, в production - webhook
    if os.getenv("ENVIRONMENT") == "development":
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
    else:
        # Запускаем Flask для обработки вебхуков
        app.run(host='0.0.0.0', port=8000)

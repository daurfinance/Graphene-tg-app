from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
import logging
from dotenv import load_dotenv
import os
import gettext
import asyncio
from solana.rpc.api import Client

# Load environment variables
load_dotenv()

# Создаем Router для регистрации хендлеров
router = Router()

# Telegram Bot Setup
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in the .env file")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()  # Dispatcher теперь создается без аргументов

# Регистрируем Router в Dispatcher
dp.include_router(router)

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

# Подключение к Solana
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
solana_client = Client(SOLANA_RPC_URL)

# Добавлены ссылки на проект и соцсети из ENV
PROJECT_WEBSITE = os.getenv("PROJECT_WEBSITE", "https://www.g3zgraphene.com/")
SOCIAL_TWITTER = os.getenv("SOCIAL_TWITTER", "https://twitter.com/example")
SOCIAL_TELEGRAM = os.getenv("SOCIAL_TELEGRAM", "https://t.me/example")

# Обновление клавиатуры для командп
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="buy"),
            KeyboardButton(text="airdrop"),
            KeyboardButton(text="stake")
        ],
        [
            KeyboardButton(text="Open WebApp"),
            KeyboardButton(text="Project Website")
        ],
        [
            KeyboardButton(text="Twitter"),
            KeyboardButton(text="Telegram")
        ]
    ],
    resize_keyboard=True
)

# Improved logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GrapheneBot")
logger.info("Bot is starting...")

# Telegram Bot Handlers
@router.message(Command(commands=['start']))
async def send_welcome(message: Message):
    await message.reply(
        _(f"Welcome to the Graphene Bot!\n\n"
          f"Project Links:\n"
          f"- Website: {PROJECT_WEBSITE}\n"
          f"- Twitter: {SOCIAL_TWITTER}\n"
          f"- Telegram: {SOCIAL_TELEGRAM}"),
        reply_markup=keyboard
    )

@router.message(Command(commands=['help']))
async def send_help(message: Message):
    await message.reply(
        _("Available commands: /start, /help, /buy, /airdrop, /stake"),
        reply_markup=keyboard
    )

@router.message(Command(commands=['buy']))
async def handle_buy(message: Message):
    # Логика покупки токенов
    await message.reply(_("You can buy tokens via the WebApp or directly here. Feature coming soon."))

@router.message(Command(commands=['airdrop']))
async def handle_airdrop(message: Message):
    # Логика участия в эйрдропе
    await message.reply(_("Airdrop participation is now available. Feature coming soon."))

@router.message(Command(commands=['stake']))
async def handle_stake(message: Message):
    # Логика стейкинга
    await message.reply(_("Staking functionality is under development."))

@router.message(lambda message: message.text == "Open WebApp")
async def open_webapp(message: Message):
    webapp_url = os.getenv('WEBAPP_URL', 'https://graphene-tg-app.vercel.app')
    await message.reply(_(f"Open the WebApp here: {webapp_url}"))

# Обработчики для новых кнопок
@router.message(lambda message: message.text == "Project Website")
async def project_website(message: Message):
    await message.reply(_(f"Visit our project website: {PROJECT_WEBSITE}"))

@router.message(lambda message: message.text == "Twitter")
async def twitter(message: Message):
    await message.reply(_(f"Follow us on Twitter: {SOCIAL_TWITTER}"))

@router.message(lambda message: message.text == "Telegram")
async def telegram(message: Message):
    await message.reply(_(f"Join our Telegram channel: {SOCIAL_TELEGRAM}"))

async def main():
    # Удаляем активный webhook перед запуском polling
    await bot.delete_webhook()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

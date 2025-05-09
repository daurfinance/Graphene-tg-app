#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Простой Telegram бот для проекта Graphene с поддержкой мультиязычности.
"""

import logging
import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import solana
from solana.rpc.async_api import AsyncClient
from solders.keypair import Keypair
from solders.transaction import Transaction
from solders.system_program import TransferParams, transfer
from database import SessionLocal, User

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения
load_dotenv()

# Токен бота
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("Пожалуйста, установите TELEGRAM_TOKEN в файле .env")

# Ссылки на проект и соцсети из ENV
PROJECT_WEBSITE = os.getenv("PROJECT_WEBSITE", "https://example.com")
SOCIAL_TWITTER = os.getenv("SOCIAL_TWITTER", "https://twitter.com/example")
SOCIAL_TELEGRAM = os.getenv("SOCIAL_TELEGRAM", "https://t.me/example")

# Инициализация бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# Инициализация клиента Solana
SOLANA_RPC_URL = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.com")
solana_client = AsyncClient(SOLANA_RPC_URL)

# Клавиатура для команд
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="/buy"),
            KeyboardButton(text="/airdrop"),
            KeyboardButton(text="/stake")
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

# Функция для получения или создания пользователя
def get_or_create_user(telegram_id: str):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    db.close()
    return user

# Пример функции для подключения кошелька
async def connect_wallet(wallet_address: str):
    try:
        # Проверка баланса кошелька
        balance = await solana_client.get_balance(wallet_address)
        return f"Ваш баланс: {balance['result']['value']} лампортов."
    except Exception as e:
        return f"Ошибка подключения кошелька: {str(e)}"

# Обработчики команд
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    """Обработчик команды /start"""
    user = get_or_create_user(message.from_user.id)
    await message.reply(
        f"Привет, {message.from_user.first_name}! Ваш текущий баланс: {user.balance} токенов.\n\n"
        f"Ссылки на проект:\n"
        f"- Вебсайт: {PROJECT_WEBSITE}\n"
        f"- Twitter: {SOCIAL_TWITTER}\n"
        f"- Telegram: {SOCIAL_TELEGRAM}",
        reply_markup=keyboard
    )

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
    """Обработчик команды /help"""
    help_text = (
        "Доступные команды:\n\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать эту справку\n"
        "/buy - Купить токены GRAPH\n"
        "/airdrop - Участвовать в эйрдропе\n"
        "/stake - Стейкинг токенов\n"
        "/wallet - Подключить кошелек Solana\n"
    )
    await message.reply(help_text)

@dp.message_handler(commands=['buy'])
async def buy_tokens(message: types.Message):
    """Логика покупки токенов"""
    await message.reply("Функция покупки токенов GRAPH будет доступна в ближайшее время!")

@dp.message_handler(commands=['airdrop'])
async def airdrop(message: types.Message):
    """Логика участия в эйрдропе"""
    wallet_address = message.text.split(maxsplit=1)[-1]
    if not wallet_address:
        await message.reply("Пожалуйста, укажите адрес вашего кошелька Solana.")
        return
    response = await connect_wallet(wallet_address)
    await message.reply(response)

@dp.message_handler(commands=['stake'])
async def stake_tokens(message: types.Message):
    """Логика стейкинга токенов"""
    await message.reply("Функция стейкинга токенов GRAPH будет доступна после подключения кошелька!")

@dp.message_handler(commands=['wallet'])
async def connect_wallet_command(message: types.Message):
    """Обработчик команды /wallet"""
    await message.reply("Для подключения кошелька Solana, пожалуйста, перейдите по ссылке: https://graphene-tg-app.vercel.app")

@dp.message_handler(lambda message: message.text == "Project Website")
async def project_website(message: types.Message):
    await message.reply(f"Посетите наш сайт: {PROJECT_WEBSITE}")

@dp.message_handler(lambda message: message.text == "Twitter")
async def twitter(message: types.Message):
    await message.reply(f"Подписывайтесь на нас в Twitter: {SOCIAL_TWITTER}")

@dp.message_handler(lambda message: message.text == "Telegram")
async def telegram(message: types.Message):
    await message.reply(f"Присоединяйтесь к нашему Telegram-каналу: {SOCIAL_TELEGRAM}")

@dp.message_handler()
async def echo(message: types.Message):
    """Обработчик всех остальных сообщений"""
    await message.reply(f"Я не понимаю эту команду. Используйте /help для получения списка команд.")

if __name__ == '__main__':
    # Запуск бота
    print("Бот Graphene запущен!")
    executor.start_polling(dp, skip_updates=True)

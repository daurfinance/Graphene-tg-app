from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.filters import Command, CommandObject
from aiogram.utils.i18n import I18n, FSMI18nMiddleware
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import logging
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables
load_dotenv()

# --- Constants ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN is not set in the .env file")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOCALES_DIR = os.path.join(BASE_DIR, 'locales')

PROJECT_WEBSITE = os.getenv("PROJECT_WEBSITE", "https://g3zgraphene.com")  # Updated
SOCIAL_TWITTER = os.getenv("SOCIAL_TWITTER", "https://twitter.com/G3zGraph")  # Updated
SOCIAL_TELEGRAM_CHANNEL = os.getenv("SOCIAL_TELEGRAM", "https://t.me/g3zgraphene")  # Updated
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://v0-solana-token-app-gilt.vercel.app/en")  # Updated

# Vercel deployment settings
APP_BASE_URL = os.getenv("VERCEL_URL")  # Vercel provides this URL automatically

# --- Language Name Mapping ---
LANG_NAME_MAP = {
    "en": "English",
    "ru": "Русский"
}

# --- Bot, Dispatcher, Router ---
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)

# --- Multilingual Support (i18n) ---
i18n = I18n(path=LOCALES_DIR, default_locale="en", domain="graphene_bot")
user_languages = {}  # In-memory storage for user language preferences

async def get_user_locale(event_from_user):
    if event_from_user is None:
        return i18n.default_locale
    return user_languages.get(event_from_user.id, i18n.default_locale)

# Register i18n middleware
dp.update.middleware(FSMI18nMiddleware(i18n))

# --- Keyboard Definitions ---
def get_main_keyboard(locale: str):
    _ = i18n.gettext
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("🚀 GrapheneApp", locale=locale), web_app=WebAppInfo(url=WEBAPP_URL))],
            [KeyboardButton(text=_("ℹ️ О Проекте", locale=locale)), KeyboardButton(text=_("🌐 Язык", locale=locale))],
            [KeyboardButton(text=_("🔗 Соц. Сети", locale=locale))],
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )

def get_about_project_keyboard(locale: str):
    _ = i18n.gettext
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("📜 Whitepaper", locale=locale)), KeyboardButton(text=_("🗺️ Дорожная карта", locale=locale))],
            [KeyboardButton(text=_("👥 Команда", locale=locale)), KeyboardButton(text=_("🌍 Наш сайт", locale=locale))],  # Added "Наш сайт" button
            [KeyboardButton(text=_("⬅️ Назад", locale=locale))]
        ],
        resize_keyboard=True
    )

def get_socials_keyboard(locale: str):
    _ = i18n.gettext
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_("🐦 Twitter", locale=locale)), KeyboardButton(text=_("✈️ Telegram Канал", locale=locale))],
            [KeyboardButton(text=_("⬅️ Назад", locale=locale))]
        ],
        resize_keyboard=True
    )

def get_language_keyboard(locale: str):
    _ = i18n.gettext
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇬🇧 English"), KeyboardButton(text="🇷🇺 Русский")],
            [KeyboardButton(text=_("⬅️ Назад", locale=locale))]
        ],
        resize_keyboard=True
    )

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("GrapheneBot")

# --- Bot Handlers ---
@router.message(Command(commands=['start', 'help']))
async def send_welcome(message: Message):
    user_id = message.from_user.id
    if user_id not in user_languages:
        user_tg_lang = message.from_user.language_code
        if user_tg_lang and user_tg_lang.startswith('ru'):
            user_languages[user_id] = 'ru'
        else:
            user_languages[user_id] = i18n.default_locale

    locale = await get_user_locale(message.from_user)
    _ = i18n.gettext

    welcome_text = _("👋 Добро пожаловать в Graphene Bot!\n\nИспользуйте кнопки ниже для навигации.", locale=locale)
    await message.reply(welcome_text, reply_markup=get_main_keyboard(locale))

@router.message(Command(commands=['language']))
async def cmd_language_command(message: Message, command: CommandObject):
    user_id = message.from_user.id
    locale = await get_user_locale(message.from_user)
    _ = i18n.gettext

    if command.args and command.args in i18n.available_locales:
        user_languages[user_id] = command.args
        new_locale = command.args
        await message.reply(
            _("Язык изменен на {lang_name}.", locale=new_locale).format(lang_name=LANG_NAME_MAP.get(new_locale, new_locale.upper())),
            reply_markup=get_main_keyboard(new_locale)
        )
    else:
        await message.reply(
            _("Пожалуйста, выберите язык:", locale=locale),
            reply_markup=get_language_keyboard(locale)
        )

@router.message(F.web_app_data)
async def web_app_data_received(message: Message):
    locale = await get_user_locale(message.from_user)
    _ = i18n.gettext
    logger.info(f"Received WebApp data: {message.web_app_data.data}")
    await message.reply(
        _("Данные из WebApp получены: {data}", locale=locale).format(data=message.web_app_data.data),
        reply_markup=get_main_keyboard(locale)
    )

# --- Navigation Handlers ---
TEXT_ABOUT_EN = "ℹ️ About Project"
TEXT_LANGUAGE_EN = "🌐 Language"
TEXT_SOCIALS_EN = "🔗 Social Media"
TEXT_WHITEPAPER_EN = "📜 Whitepaper"
TEXT_ROADMAP_EN = "🗺️ Roadmap"
TEXT_TEAM_EN = "👥 Team"
TEXT_OUR_WEBSITE_EN = "🌍 Our Website"  # New constant
TEXT_TWITTER_EN = "🐦 Twitter"  # Added definition
TEXT_TELEGRAM_CHANNEL_EN = "✈️ Telegram Channel"  # Added definition
TEXT_BACK_EN = "⬅️ Back"
TEXT_LANG_EN_BUTTON = "🇬🇧 English"
TEXT_LANG_RU_BUTTON = "🇷🇺 Русский"

@router.message()
async def handle_text_buttons(message: Message):
    user_id = message.from_user.id
    locale = user_languages.get(user_id, i18n.default_locale)
    _ = i18n.gettext

    if message.text == _(TEXT_ABOUT_EN, locale=locale):
        await message.reply(_("Раздел 'О Проекте'. Выберите опцию:", locale=locale),
                            reply_markup=get_about_project_keyboard(locale))
    elif message.text == _(TEXT_WHITEPAPER_EN, locale=locale):
        await send_long_message(message.chat.id, bot, WHITEPAPER_CONTENT.get(locale, WHITEPAPER_CONTENT['en']))
        await message.reply(_("Whitepaper был отправлен. Выберите другую опцию или вернитесь назад:", locale=locale), reply_markup=get_about_project_keyboard(locale))
    elif message.text == _(TEXT_ROADMAP_EN, locale=locale):
        await send_long_message(message.chat.id, bot, ROADMAP_CONTENT.get(locale, ROADMAP_CONTENT['en']))
        await message.reply(_("Дорожная карта была отправлена. Выберите другую опцию или вернитесь назад:", locale=locale), reply_markup=get_about_project_keyboard(locale))
    elif message.text == _(TEXT_TEAM_EN, locale=locale):
        await send_long_message(message.chat.id, bot, TEAM_CONTENT.get(locale, TEAM_CONTENT['en']))
        await message.reply(_("Информация о команде была отправлена. Выберите другую опцию или вернитесь назад:", locale=locale), reply_markup=get_about_project_keyboard(locale))
    elif message.text == _(TEXT_OUR_WEBSITE_EN, locale=locale):  # Handler for "Our Website"
        await message.reply(_("Посетите наш сайт: {url}", locale=locale).format(url=PROJECT_WEBSITE),
                            reply_markup=get_about_project_keyboard(locale))
    elif message.text == _(TEXT_SOCIALS_EN, locale=locale):
        await message.reply(_("Наши социальные сети:", locale=locale),
                            reply_markup=get_socials_keyboard(locale))
    elif message.text == _(TEXT_TWITTER_EN, locale=locale):
        await message.reply(_("Наш Twitter: {url}", locale=locale).format(url=SOCIAL_TWITTER),
                            reply_markup=get_socials_keyboard(locale))
    elif message.text == _(TEXT_TELEGRAM_CHANNEL_EN, locale=locale):
        await message.reply(_("Наш Telegram канал: {url}", locale=locale).format(url=SOCIAL_TELEGRAM_CHANNEL),
                            reply_markup=get_socials_keyboard(locale))
    elif message.text == _(TEXT_LANGUAGE_EN, locale=locale):
        await message.reply(_("Пожалуйста, выберите язык:", locale=locale),
                            reply_markup=get_language_keyboard(locale))
    elif message.text == TEXT_LANG_EN_BUTTON:
        user_languages[user_id] = "en"
        new_locale = "en"
        await message.reply(
            _("Язык изменен на {lang_name}.", locale=new_locale).format(lang_name=LANG_NAME_MAP.get(new_locale, new_locale.upper())),
            reply_markup=get_main_keyboard(new_locale)
        )
    elif message.text == TEXT_LANG_RU_BUTTON:
        user_languages[user_id] = "ru"
        new_locale = "ru"
        await message.reply(
            _("Язык изменен на {lang_name}.", locale=new_locale).format(lang_name=LANG_NAME_MAP.get(new_locale, new_locale.upper())),
            reply_markup=get_main_keyboard(new_locale)
        )
    elif message.text == _(TEXT_BACK_EN, locale=locale):
        await message.reply(_("Главное меню.", locale=locale),
                            reply_markup=get_main_keyboard(locale))

# --- Vercel Webhook Setup ---
async def on_startup(dispatcher: Dispatcher):
    webhook_url = f"https://{APP_BASE_URL}/webhook/{TELEGRAM_TOKEN}"
    await bot.set_webhook(webhook_url)
    logger.info(f"Webhook set to: {webhook_url}")

async def on_shutdown(dispatcher: Dispatcher):
    logger.warning('Shutting down..')
    await bot.delete_webhook()
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()
    logger.warning('Bye!')

app = web.Application()
SimpleRequestHandler(dispatcher=dp, bot=bot).register(app, path=f"/webhook/{TELEGRAM_TOKEN}")
setup_application(app, dp, bot=bot)

# Helper function to send long messages
async def send_long_message(chat_id: int, bot_instance: Bot, text: str, max_length: int = 4096):
    """Splits a long message into parts and sends them."""
    for i in range(0, len(text), max_length):
        await bot_instance.send_message(chat_id, text[i:i + max_length])

# --- Content Constants ---
WHITEPAPER_CONTENT = {
    "en": """White Paper for Graphene (GRAPH)
Date: April 1, 2025

Table of Contents
1. Introduction
2. Problem Statement
3. Solution
4. Token Specifications
5. Token Allocation
6. Roadmap
7. Team
8. Token Economics
9. Contracts & Security
10. Graphene Overview: History, Properties & Applications
11. Production Processes & Innovation
12. Markets & Applications
13. Investment Requirements
14. Risk & Mitigation
15. Conclusion
16. Contacts

1. Introduction
Graphene (GRAPH) is a utility token built on the Solana blockchain designed to fund the
scaling of single-layer graphene production — a revolutionary material with exceptional
properties.

2. Problem Statement
Current graphene production costs (~$25/g), limited industrial capacity, and supply shortages
hinder innovation in electronics, energy storage, medicine, and composite materials.

3. Solution
GRAPH creates a decentralized funding mechanism and ensures sustained demand: graphene
products can only be purchased using GRAPH tokens, aligning token value with real-world
production and demand.

4. Token Specifications
• Name: Graphene
• Symbol: GRAPH
• Blockchain: Solana (SPL Token)
• Total Supply: 100,000,000,000 GRAPH

5. Token Allocation
Category Amount Percentage Vesting Schedule
Investment Funding 500,000,000 50% 6-month cliff, 24-month linear vesting
Project Development 100,000,000 10% 12 months
Team 100,000,000 10% 12-month cliff, 24-month linear vesting
Reserve 200,000,000 20% N/A
Marketing & Partnerships 100,000,000 10% N/A

6. Roadmap
Date Milestone Description
Apr 1, 2025 Project Launch PR campaign & marketing preparation
Apr 7, 2025 Team Formation Hiring key personnel
Apr 14, 2025 Token Sale Launch Public sale of GRAPH tokens
Apr 30, 2025 Initial Results Sales analysis & investor report
May 1, 2025 Production Financing Fundraising for R&D center & certification
Q3 2025 EU Production Certification & pilot line launch
Q4 2025 UAE Production Establishment of manufacturing line
Q1 2026 Singapore Production Full-scale production launch in Asia

7. Team
Name Role Expertise
Vyacheslav Korchagin CEO Founder Finance & project management
Alexander Moor Partner Intellectual property & product strategy

8. Token Economics
GRAPH aligns token value with the production and sale of high-quality graphene, ensuring
demand-driven appreciation and investor returns.

9. Contracts & Security
The GRAPH smart contract undergoes third-party audit. Real-time production, sales, and
financial reports will be publicly available on the project website.

10. Graphene Overview: History, Properties & Applications
Graphene, first isolated in 2004, is a single-atom-thick carbon lattice with unparalleled
strength, conductivity, and flexibility. Applications span electronics, supercapacitors,
composites, water filtration, biomedical devices, and construction materials.

11. Production Processes & Innovation
Our proprietary thermomechanical and ultrasonic exfoliation methods yield few-layer
graphene with minimal defects at cost-effective rates (~€1/g). Scalable processes include
catalytic CVD and plasma-enhanced CVD (PE-CVD) for large-area production.
Quality Control (Raman Spectroscopy)
Raman analysis confirms average layer count of 2–3 and low defectiveness (ID/IG) for
ultrasonic exfoliation, while disintegrator methods deliver higher throughput (0.5–1 kg/h)
with moderate layer count and low defects.
Method Avg. Layers ID/IG Throughput Advantage
Ultrasonic Exfoliation 2–3 Low 0.3–0.5 g/h Highest quality
Ultrasonic + Mechanical 4–6 High 0.3–0.5 g/h —
Disintegrator >5 Low 0.5–1 kg/h Scalability

12. Markets & Applications
Graphene’s diverse applications include:
Sector Use Cases
Electronics Sensors, semiconductors
Energy Supercapacitors, batteries
Composites Automotive, aerospace
Water Treatment Filtration membranes
Healthcare Biosensors, diagnostics
Construction Fire-resistant insulation

13. Investment Requirements
€27M required to build two production lines (12.5 kg/h each) covering equipment,
certification, operations, staffing, and go-to-market activities.

14. Risk & Mitigation
Risk Mitigation
Regulatory delays Comprehensive compliance in each jurisdiction
Technical challenges Partnerships with leading R&D institutes
Demand volatility Product & market diversification
Competitive threats Proprietary technology & IP protection

15. Conclusion
GRAPH presents a unique opportunity to invest in a game-changing graphene production
technology. Join us to capitalize on the growth of a multi-billion-dollar market while driving
real-world innovation.

16. Contacts
• Twitter: @G3zGraph
• Telegram: @g3zgraphene
• Website: https://g3zgraphene.com
• Email: g3z.graphene@gmail.com
""",
    "ru": """White Paper для Graphene (GRAPH)
Дата: 1 апреля 2025 г.

Содержание
1. Введение
2. Постановка проблемы
3. Решение
4. Спецификации токена
5. Распределение токенов
6. Дорожная карта
7. Команда
8. Экономика токена
9. Контракты и безопасность
10. Обзор графена: история, свойства и применение
11. Производственные процессы и инновации
12. Рынки и применение
13. Инвестиционные потребности
14. Риски и их снижение
15. Заключение
16. Контакты

1. Введение
Graphene (GRAPH) — это служебный токен, созданный на блокчейне Solana и предназначенный для финансирования
масштабирования производства однослойного графена — революционного материала с исключительными
свойствами.

2. Постановка проблемы
Текущие затраты на производство графена (~$25/г), ограниченные промышленные мощности и нехватка поставок
препятствуют инновациям в электронике, хранении энергии, медицине и композитных материалах.

3. Решение
GRAPH создает децентрализованный механизм финансирования и обеспечивает устойчивый спрос: графеновые
продукты можно приобрести только за токены GRAPH, что увязывает стоимость токена с реальным
производством и спросом.

4. Спецификации токена
• Название: Graphene
• Символ: GRAPH
• Блокчейн: Solana (SPL Token)
• Общее предложение: 100,000,000,000 GRAPH

5. Распределение токенов
Категория Количество Процент График вестинга
Инвестиционное финансирование 500,000,000 50% 6-месячный клифф, 24-месячный линейный вестинг
Разработка проекта 100,000,000 10% 12 месяцев
Команда 100,000,000 10% 12-месячный клифф, 24-месячный линейный вестинг
Резерв 200,000,000 20% Н/Д
Маркетинг и партнерства 100,000,000 10% Н/Д

6. Дорожная карта
Дата Этап Описание
1 апр 2025 Запуск проекта PR-кампания и подготовка к маркетингу
7 апр 2025 Формирование команды Наем ключевого персонала
14 апр 2025 Запуск продажи токенов Публичная продажа токенов GRAPH
30 апр 2025 Первые результаты Анализ продаж и отчет для инвесторов
1 мая 2025 Финансирование производства Сбор средств на НИОКР-центр и сертификацию
3 кв. 2025 Производство в ЕС Сертификация и запуск пилотной линии
4 кв. 2025 Производство в ОАЭ Создание производственной линии
1 кв. 2026 Производство в Сингапуре Запуск полномасштабного производства в Азии

7. Команда
Имя Роль Экспертиза
Вячеслав Корчагин CEO Основатель Финансы и управление проектами
Александр Моор Партнер Интеллектуальная собственность и продуктовая стратегия

8. Экономика токена
GRAPH увязывает стоимость токена с производством и продажей высококачественного графена, обеспечивая
рост, обусловленный спросом, и доходность для инвесторов.

9. Контракты и безопасность
Смарт-контракт GRAPH проходит аудит третьей стороной. Отчеты о производстве, продажах и
финансовые отчеты в реальном времени будут общедоступны на веб-сайте проекта.

10. Обзор графена: история, свойства и применение
Графен, впервые выделенный в 2004 году, представляет собой одноатомную углеродную решетку с непревзойденной
прочностью, проводимостью и гибкостью. Применение охватывает электронику, суперконденсаторы,
композиты, фильтрацию воды, биомедицинские устройства и строительные материалы.

11. Производственные процессы и инновации
Наши запатентованные методы термомеханической и ультразвуковой эксфолиации позволяют получать малослойный
графен с минимальными дефектами по экономически выгодным ценам (~€1/г). Масштабируемые процессы включают
каталитическое CVD и плазменно-усиленное CVD (PE-CVD) для производства больших площадей.
Контроль качества (рамановская спектроскопия)
Рамановский анализ подтверждает среднее количество слоев 2–3 и низкую дефектность (ID/IG) для
ультразвуковой эксфолиации, в то время как методы с использованием дезинтегратора обеспечивают более высокую производительность (0.5–1 кг/ч)
при умеренном количестве слоев и низкой дефектности.
Метод Среднее кол-во слоев ID/IG Производительность Преимущество
Ультразвуковая эксфолиация 2–3 Низкая 0.3–0.5 г/ч Высочайшее качество
Ультразвуковая + механическая 4–6 Высокая 0.3–0.5 г/ч —
Дезинтегратор >5 Низкая 0.5–1 кг/ч Масштабируемость

12. Рынки и применение
Разнообразные области применения графена включают:
Сектор Примеры использования
Электроника Датчики, полупроводники
Энергетика Суперконденсаторы, батареи
Композиты Автомобилестроение, аэрокосмическая промышленность
Очистка воды Фильтрационные мембраны
Здравоохранение Биосенсоры, диагностика
Строительство Огнестойкая изоляция

13. Инвестиционные потребности
Требуется €27 млн для строительства двух производственных линий (по 12.5 кг/ч каждая), включая оборудование,
сертификацию, операционные расходы, персонал и вывод на рынок.

14. Риски и их снижение
Риск Снижение
Регуляторные задержки Всестороннее соблюдение требований в каждой юрисдикции
Технические проблемы Партнерство с ведущими НИИ
Волатильность спроса Диверсификация продуктов и рынков
Конкурентные угрозы Запатентованная технология и защита ИС

15. Заключение
GRAPH представляет уникальную возможность инвестировать в революционную технологию производства графена.
Присоединяйтесь к нам, чтобы извлечь выгоду из роста многомиллиардного рынка и способствовать
реальным инновациям.

16. Контакты
• Twitter: @G3zGraph
• Telegram: @g3zgraphene
• Веб-сайт: https://g3zgraphene.com
• Email: g3z.graphene@gmail.com
"""
}

ROADMAP_CONTENT = {
    "en": """6. Roadmap
Date Milestone Description
Apr 1, 2025 Project Launch PR campaign & marketing preparation
Apr 7, 2025 Team Formation Hiring key personnel
Apr 14, 2025 Token Sale Launch Public sale of GRAPH tokens
Apr 30, 2025 Initial Results Sales analysis & investor report
May 1, 2025 Production Financing Fundraising for R&D center & certification
Q3 2025 EU Production Certification & pilot line launch
Q4 2025 UAE Production Establishment of manufacturing line
Q1 2026 Singapore Production Full-scale production launch in Asia""",
    "ru": """6. Дорожная карта
Дата Этап Описание
1 апр 2025 Запуск проекта PR-кампания и подготовка к маркетингу
7 апр 2025 Формирование команды Наем ключевого персонала
14 апр 2025 Запуск продажи токенов Публичная продажа токенов GRAPH
30 апр 2025 Первые результаты Анализ продаж и отчет для инвесторов
1 мая 2025 Финансирование производства Сбор средств на НИОКР-центр и сертификацию
3 кв. 2025 Производство в ЕС Сертификация и запуск пилотной линии
4 кв. 2025 Производство в ОАЭ Создание производственной линии
1 кв. 2026 Производство в Сингапуре Запуск полномасштабного производства в Азии"""
}

TEAM_CONTENT = {
    "en": """7. Team
Name Role Expertise
Vyacheslav Korchagin CEO Founder Finance & project management
Alexander Moor Partner Intellectual property & product strategy""",
    "ru": """7. Команда
Имя Роль Экспертиза
Вячеслав Корчагин CEO Основатель Финансы и управление проектами
Александр Моор Партнер Интеллектуальная собственность и продуктовая стратегия"""
}

# --- Main execution ---
async def run_polling():
    logger.info("Starting bot in polling mode...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())

if __name__ == "__main__":
    if not APP_BASE_URL:
        asyncio.run(run_polling())
    else:
        logger.info("Webhook setup for Vercel. Vercel will run the aiohttp app.")

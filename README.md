# Graphene Telegram Bot

This project is a Telegram bot for the Graphene project, providing users with information about the project, its whitepaper, roadmap, team, and social media links. The bot supports multiple languages (English and Russian).

## Features

*   **Multilingual Support**: Switch between English and Russian.
*   **Main Menu**:
    *   🚀 **GrapheneApp**: Opens the Graphene web application.
    *   ℹ️ **About Project**: Access detailed project information.
    *   🌐 **Language**: Change the bot's language.
    *   🔗 **Social Media**: Find links to Graphene's social channels.
*   **About Project Section**:
    *   📜 **Whitepaper**: Displays the full project whitepaper.
    *   🗺️ **Roadmap**: Shows the project roadmap.
    *   👥 **Team**: Provides information about the team.
    *   🌍 **Our Website**: Links to the official Graphene website.
*   **Social Media Section**: Links to Twitter and Telegram.

## Deployment

The bot is designed for deployment on Vercel.

## Setup (for local development)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd Graphene-tg-app
    ```
2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up environment variables:**
    Create a `.env` file in the root directory with your Telegram Bot Token:
    ```
    TELEGRAM_BOT_TOKEN=YOUR_ACTUAL_BOT_TOKEN
    ```
5.  **Compile language files:**
    If you make changes to the `.po` files in the `locales` directory, you need to compile them:
    ```bash
    pybabel compile -d locales -D graphene_bot
    ```
6.  **Run the bot (optional - primarily for webhook setup with a tool like ngrok for local testing):**
    The bot is set up to run via webhooks for Vercel. For local testing of the webhook logic, you might need a tool like ngrok.
    The `main.py` script can be run directly, but it's configured to start an `aiohttp` web server for the webhook.

    To run the bot locally using polling (for development purposes, requires modifying `main.py` to use polling instead of webhooks):
    ```python
    # Example modification in main.py for local polling
    # Comment out webhook setup and uncomment/add:
    # await dp.start_polling(bot)
    ```

## Project Structure

```
Graphene-tg-app/
├── .git/
├── .gitignore
├── .vscode/
├── locales/                # Localization files
│   ├── en/LC_MESSAGES/
│   │   ├── graphene_bot.mo # Compiled translations (English)
│   │   └── graphene_bot.po # Translation sources (English)
│   └── ru/LC_MESSAGES/
│       ├── graphene_bot.mo # Compiled translations (Russian)
│       └── graphene_bot.po # Translation sources (Russian)
├── .env                    # Environment variables (ignored by git)
├── main.py                 # Main application logic for the Telegram bot
├── README.md               # This file
├── requirements.txt        # Python dependencies
└── vercel.json             # Vercel deployment configuration
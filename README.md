# Graphene-tg-app

## Telegram Bot for Graphene (GRAPH) Token

This repository contains a Telegram bot for the Graphene (GRAPH) token. The bot provides a web interface with wallet connect in the Solana network. The interface is beautiful and includes a personal account, sections, an Airdrop section, and the ability to buy tokens.

### Features

- Web interface with wallet connect in the Solana network
- Beautiful interface with personal account and sections
- Airdrop section for token distribution
- Ability to buy tokens

### Setup and Run

1. Clone the repository:
   ```bash
   git clone https://github.com/daurfinance/Graphene-tg-app.git
   cd Graphene-tg-app
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token
   - `SOLANA_NETWORK_URL`: URL of the Solana network
   - `GRAPHENE_TOKEN_ADDRESS`: Address of the Graphene (GRAPH) token

4. Run the bot:
   ```bash
   python bot.py
   ```

### Web Interface

The web interface allows users to connect their wallets in the Solana network, manage their personal accounts, and access various sections including the Airdrop section and the token purchase section.

### Airdrop Section

The Airdrop section allows users to participate in token distributions. Users can view available airdrops and claim their tokens.

### Token Purchase

The bot provides an option for users to buy Graphene (GRAPH) tokens. Users can view their balance and make transactions directly through the bot.

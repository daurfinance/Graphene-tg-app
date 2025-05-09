from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_babel import Babel, gettext as _
import os

# Flask Setup
app = Flask(__name__)

# Настройка Babel для мультиязычности
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'locales'
app.config['BABEL_DEFAULT_DOMAIN'] = 'graphene_bot' # Добавлено для указания домена
babel = Babel(app)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(['en', 'ru'])

# Improved logging setup
@app.route("/", methods=["GET"])
def read_root():
    return render_template("index.html", message="Welcome to the Graphene Web Interface!")

@app.route("/buy", methods=["GET"])
def buy_page():
    return render_template("buy.html", message="Buy tokens securely using your wallet.")

@app.route("/airdrop", methods=["GET"])
def airdrop_page():
    return render_template("airdrop.html", message="Participate in the airdrop and claim your tokens.")

@app.route("/stake", methods=["GET"])
def stake_page():
    return render_template("stake.html", message="Stake your tokens and earn rewards.")

@app.route("/connect-wallet", methods=["POST"])
def connect_wallet():
    wallet_address = request.form.get("wallet_address")
    if wallet_address:
        return jsonify({"message": f"Wallet {wallet_address} connected successfully!"})
    return jsonify({"error": "Wallet address is required."}), 400

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

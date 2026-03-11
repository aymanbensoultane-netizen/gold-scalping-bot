import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
import requests

TELEGRAM_TOKEN   = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
PORT             = int(os.environ.get("PORT", 5000))
SECRET_KEY       = "goldscalping2024"

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

def send_telegram(message):
    url = "https://api.telegram.org/bot{}/sendMessage".format(TELEGRAM_TOKEN)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        logger.info("Message Telegram envoye avec succes")
        return True
    except Exception as e:
        logger.error("Erreur Telegram : {}".format(e))
        return False

def format_signal(data):
    signal  = data.get("signal", "?")
    symbol  = data.get("symbol", "XAUUSD")
    price   = data.get("price", "?")
    sl      = data.get("sl", "?")
    tp      = data.get("tp", "?")
    time_   = data.get("time", datetime.now().strftime("%H:%M:%S"))

    emoji   = "GREEN" if signal == "BUY" else "RED"
    action  = "ACHAT" if signal == "BUY" else "VENTE"

    return """
{} SIGNAL {} - {}

Prix actuel : {}
Stop Loss : {}
Take Profit : {}
Heure : {}

Strategie : EMA9/21 + RSI - Scalping 1-5min
Toujours verifier le marche avant d entrer !
""".format(emoji, action, symbol, price, sl, tp, time_)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        raw = request.get_data(as_text=True)
        logger.info("Signal recu : {}".format(raw))
        data = json.loads(raw)
        signal = data.get("signal", "").upper()
        if signal not in ("BUY", "SELL"):
            return jsonify({"error": "Signal invalide"}), 400
        message = format_signal(data)
        success = send_telegram(message)
        if success:
            return jsonify({"status": "ok", "signal": signal}), 200
        else:
            return jsonify({"error": "Echec envoi Telegram"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "JSON invalide"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    send_telegram("Bot Gold Scalping actif !\nConnexion Telegram OK\nEn attente de signaux TradingView...")
    return jsonify({"status": "Bot actif", "telegram": "Message de test envoye"}), 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "bot": "Gold Scalping Bot",
        "status": "En ligne",
        "endpoints": {
            "/webhook": "POST - Recoit les signaux TradingView",
            "/test": "GET - Teste la connexion Telegram"
        }
    }), 200

if __name__ == "__main__":
    logger.info("Demarrage du bot Gold Scalping...")
    app.run(host="0.0.0.0", port=PORT, debug=False)

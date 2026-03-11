import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_telegram(message):
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error("Erreur: " + str(e))
        return False

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = json.loads(request.get_data(as_text=True))
        signal = data.get("signal", "").upper()
        if signal not in ("BUY", "SELL"):
            return jsonify({"error": "invalide"}), 400
        send_telegram("SIGNAL " + signal + " XAUUSD\nPrix: " + data.get("price","?"))
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    send_telegram("Bot Gold actif!")
    return jsonify({"status": "ok"}), 200

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "en ligne"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=False)

import json
import logging
import os
from flask import Flask, request, jsonify
import requests

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
PORT = int(os.environ.get("PORT", 5000))

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def envoyer_telegram(message):
url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + "/sendMessage"
payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
try:
resp = requests.post(url, json=payload, timeout=10)
resp.raise_for_status()
return True
except Exception as e:
logger.error("Erreur : " + str(e))
return False

@app.route("/webhook", methods=["POST"])
def webhook():
try:
donnees = json.loads(request.get_data(as_text=True))
signal = donnees.get("signal", "").upper()
if signal not in ("BUY", "SELL"):
return jsonify({"erreur": "invalide"}), 400

prix = float(donnees.get("price", 0))

# Calcul TP/SL automatique (ATR simulé ~2.5 points sur Gold 5M)
atr = 2.5
if signal == "BUY":
tp = round(prix + (atr * 2), 3)
sl = round(prix - (atr * 1), 3)
emoji = "🟢"
else:
tp = round(prix - (atr * 2), 3)
sl = round(prix + (atr * 1), 3)
emoji = "🔴"

message = (
f"{emoji} SIGNAL {signal} XAUUSD\n"
f"💰 Prix : {prix}\n"
f"✅ TP : {tp}\n"
f"❌ SL : {sl}\n"
f"📊 Ratio R/R : 1:2"
)

envoyer_telegram(message)
return jsonify({"statut": "ok"}), 200
except Exception as e:
return jsonify({"erreur": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
envoyer_telegram("Bot Gold actif !")
return jsonify({"statut": "ok"}), 200

@app.route("/", methods=["GET"])
def maison():
return jsonify({"statut": "en ligne"}), 200

if __name__ == "__main__":
app.run(host="0.0.0.0", port=PORT, debug=False)

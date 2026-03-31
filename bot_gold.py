import json
import logging
import os
from datetime import datetime, timezone
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

        # FILTRE SESSION
        heure_utc = datetime.now(timezone.utc).hour
        london = 7 <= heure_utc < 12
        newyork = 13 <= heure_utc < 20
        if not (london or newyork):
            return jsonify({"statut": "hors session"}), 200

        prix = float(donnees.get("price", 0))
        
        # TP/SL ADAPTES 2 LOTS FTMO
        sl_points = 25
        tp1_points = 50
        tp2_points = 100

        if signal == "BUY":
            sl = round(prix - sl_points, 3)
            tp1 = round(prix + tp1_points, 3)
            tp2 = round(prix + tp2_points, 3)
            emoji = "🟢"
        else:
            sl = round(prix + sl_points, 3)
            tp1 = round(prix - tp1_points, 3)
            tp2 = round(prix - tp2_points, 3)
            emoji = "🔴"

        # CALCUL EN DOLLARS (2 lots)
        sl_dollars = sl_points * 20
        tp1_dollars = tp1_points * 20
        tp2_dollars = tp2_points * 20

        message = (
            f"{emoji} SIGNAL {signal} XAUUSD\n"
            f"💰 Entrée : {prix}\n"
            f"❌ SL : {sl} (-{sl_points} pts / -{sl_dollars}$)\n"
            f"✅ TP1 : {tp1} (+{tp1_points} pts / +{tp1_dollars}$)\n"
            f"✅ TP2 : {tp2} (+{tp2_points} pts / +{tp2_dollars}$)\n"
            f"📊 Ratio R/R : 1:2\n"
            f"⚠️ Risque : -{sl_dollars}$ max\n"
            f"🕐 Heure UTC : {heure_utc}h"
        )

        envoyer_telegram(message)
        return jsonify({"statut": "ok"}), 200
    except Exception as e:
        return jsonify({"erreur": str(e)}), 500

@app.route("/test", methods=["GET"])
def test():
    envoyer_telegram("Bot Gold actif !")
    return jsonify({"statut": "ok"}​​​​​​​​​​​​​​​​

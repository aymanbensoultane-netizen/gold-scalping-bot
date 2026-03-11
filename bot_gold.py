“””
╔══════════════════════════════════════════════════════╗
║     BOT GOLD SCALPING - Webhook → Telegram           ║
║     Reçoit les signaux TradingView et les envoie     ║
║     sur Telegram avec SL/TP et conseils              ║
╚══════════════════════════════════════════════════════╝

INSTALLATION :
pip install flask requests python-telegram-bot

LANCEMENT :
python bot_gold.py
“””

import json
import logging
import os
from datetime import datetime
from flask import Flask, request, jsonify
import requests

# ═══════════════════════════════════════

# ⚙️  CONFIGURATION — À REMPLIR !

# ═══════════════════════════════════════

 TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")    # Via @BotFather sur Telegram
 TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")   # Via @userinfobot sur Telegram
PORT             = 5000                         # Port du serveur webhook
SECRET_KEY       = “goldscalping2024”           # Clé secrète (optionnel)

# ═══════════════════════════════════════

# INITIALISATION

# ═══════════════════════════════════════

app = Flask(**name**)
logging.basicConfig(
level=logging.INFO,
format=”%(asctime)s [%(levelname)s] %(message)s”
)
logger = logging.getLogger(**name**)

# ═══════════════════════════════════════

# ENVOI TELEGRAM

# ═══════════════════════════════════════

def send_telegram(message: str):
“”“Envoie un message formaté sur Telegram.”””
url = f”https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage”
payload = {
“chat_id”: TELEGRAM_CHAT_ID,
“text”: message,
“parse_mode”: “HTML”
}
try:
resp = requests.post(url, json=payload, timeout=10)
resp.raise_for_status()
logger.info(“✅ Message Telegram envoyé avec succès”)
return True
except Exception as e:
logger.error(f”❌ Erreur Telegram : {e}”)
return False

# ═══════════════════════════════════════

# FORMATAGE DU SIGNAL

# ═══════════════════════════════════════

def format_signal(data: dict) -> str:
“”“Formate le signal en message Telegram lisible.”””
signal  = data.get(“signal”, “?”)
symbol  = data.get(“symbol”, “XAUUSD”)
price   = data.get(“price”, “?”)
sl      = data.get(“sl”, “?”)
tp      = data.get(“tp”, “?”)
time_   = data.get(“time”, datetime.now().strftime(”%H:%M:%S”))

```
emoji   = "🟢" if signal == "BUY" else "🔴"
action  = "ACHAT" if signal == "BUY" else "VENTE"
conseil = "Cherche un retrace sur EMA9 pour entrer." if signal == "BUY" else "Attends une résistance pour confirmer."

return f"""
```

{emoji} <b>SIGNAL {action} — {symbol}</b>

💰 <b>Prix actuel :</b> {price}
🛑 <b>Stop Loss :</b> {sl}
🎯 <b>Take Profit :</b> {tp}
🕐 <b>Heure :</b> {time_}

📌 <i>Stratégie : EMA9/21 + RSI — Scalping 1-5min</i>
💡 <i>{conseil}</i>

⚠️ <i>Toujours vérifier le marché avant d’entrer !</i>
“””

# ═══════════════════════════════════════

# ROUTES

# ═══════════════════════════════════════

@app.route(”/webhook”, methods=[“POST”])
def webhook():
“”“Endpoint principal — reçoit les alertes de TradingView.”””
try:
# Récupère les données JSON
raw = request.get_data(as_text=True)
logger.info(f”📩 Signal reçu : {raw}”)

```
    data = json.loads(raw)
    signal = data.get("signal", "").upper()

    if signal not in ("BUY", "SELL"):
        return jsonify({"error": "Signal invalide"}), 400

    # Formate et envoie sur Telegram
    message = format_signal(data)
    success = send_telegram(message)

    if success:
        return jsonify({"status": "ok", "signal": signal}), 200
    else:
        return jsonify({"error": "Échec envoi Telegram"}), 500

except json.JSONDecodeError:
    logger.error("❌ JSON invalide reçu")
    return jsonify({"error": "JSON invalide"}), 400
except Exception as e:
    logger.error(f"❌ Erreur inattendue : {e}")
    return jsonify({"error": str(e)}), 500
```

@app.route(”/test”, methods=[“GET”])
def test():
“”“Route de test — vérifie que le bot tourne.”””
send_telegram(“🤖 <b>Bot Gold Scalping actif !</b>\n✅ Connexion Telegram OK\n📡 En attente de signaux TradingView…”)
return jsonify({“status”: “Bot actif”, “telegram”: “Message de test envoyé”}), 200

@app.route(”/”, methods=[“GET”])
def home():
return jsonify({
“bot”: “Gold Scalping Bot”,
“status”: “🟢 En ligne”,
“endpoints”: {
“/webhook”: “POST - Reçoit les signaux TradingView”,
“/test”: “GET - Teste la connexion Telegram”
}
}), 200

# ═══════════════════════════════════════

# DÉMARRAGE

# ═══════════════════════════════════════

if **name** == “**main**”:
logger.info(“🚀 Démarrage du bot Gold Scalping…”)
logger.info(f”📡 Serveur sur le port {PORT}”)
logger.info(“➡️  Webhook URL : http://TON-IP:{PORT}/webhook”)
app.run(host=“0.0.0.0”, port=PORT, debug=False)

import os
import requests
import sys

# === Récupération des secrets depuis GitHub Actions ===
TAAPI_KEY = os.getenv("TAAPI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Vérification des secrets
missing = [var for var, value in {
    "TAAPI_KEY": TAAPI_KEY,
    "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
    "CHAT_ID": CHAT_ID
}.items() if not value]
if missing:
    print(f"❌ Erreur : secrets manquants -> {', '.join(missing)}")
    sys.exit(1)

# === Fonctions ===
def send_telegram(message: str):
    """Envoie un message Telegram."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Erreur envoi Telegram: {r.text}")
        else:
            print("✅ Message Telegram envoyé")
    except Exception as e:
        print(f"⚠️ Exception Telegram: {e}")

def get_bulk_prices(symbols):
    """Récupère les prix de plusieurs cryptos en un seul appel CoinGecko."""
    ids_map = {"BTC": "bitcoin", "ETH": "ethereum"}
    ids_str = ",".join(ids_map[sym] for sym in symbols)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"
    data = requests.get(url, timeout=20).json()

    prices = {}
    for sym in symbols:
        coin_id = ids_map[sym]
        if coin_id in data and "_

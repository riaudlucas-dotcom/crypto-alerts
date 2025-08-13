import os
import requests
import sys

# === Récupération des secrets depuis GitHub Actions ===
TAAPI_KEY = os.getenv("TAAPI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Vérification des variables essentielles
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
    """Envoie un message Telegram via Bot API."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Erreur envoi Telegram: {r.text}")
    except Exception as e:
        print(f"⚠️ Exception Telegram: {e}")

def get_price(symbol: str) -> float:
    """Récupère le prix en USD depuis CoinGecko."""
    ids = {
        "BTC": "bitcoin",
        "ETH": "ethereum"
    }
    symbol = symbol.upper()
    if symbol not in ids:
        raise ValueError(f"Symbole non supporté: {symbol}")

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids[symbol]}&vs_currencies=usd"
    data = requests.get(url, timeout=20).json()

    if ids[symbol] not in data or "usd" not in data[ids[symbol]]:
        raise KeyError(f"Clé '{ids[symbol]}' introuvable dans la réponse API : {data}")

    return data[ids[symbol]]["usd"]

def get_rsi(symbol: str, interval="1w") -> float:
    """Récupère le RSI depuis TAAPI.io."""
    url = (
        f"https://api.taapi.io/rsi"
        f"?secret={TAAPI_KEY}"
        f"&exchange=binance"
        f"&symbol={symbol.upper()}/USDT"
        f"&interval={interval}"
    )
    data = requests.get(url, timeout=20).json()
    if "value" not in data:
        raise ValueError(f"Erreur TAAPI.io: {data}")
    return data["value"]

# === Script principal ===
def main():
    actifs = ["BTC", "ETH"]
    paliers = {
        "BTC"

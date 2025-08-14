import os
import requests
import sys
import json
import urllib.parse

# === Récupération des secrets ===
TAAPI_KEY = os.getenv("TAAPI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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
    """Envoie un message Telegram"""
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

def get_bulk_rsi():
    """Récupère RSI BTC et ETH en un seul appel via TAAPI.io Bulk"""
    construct_payload = {
        "indicators": [
            {"indicator": "rsi", "exchange": "binance", "symbol": "BTC/USDT", "interval": "1w"},
            {"indicator": "rsi", "exchange": "binance", "symbol": "ETH/USDT", "interval": "1w"}
        ]
    }
    encoded = urllib.parse.quote(json.dumps(construct_payload))
    url = f"https://api.taapi.io/bulk?secret={TAAPI_KEY}&construct={encoded}"

    data = requests.get(url, timeout=20).json()
    if not isinstance(data, dict) or "data" not in data:
        raise ValueError(f"Réponse TAAPI.io invalide : {data}")
    return data["data"]

def get_prices():
    """Récupère prix BTC et ETH depuis CoinGecko"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd"
    data = requests.get(url, timeout=20).json()
    if "bitcoin" not in data or "ethereum" not in data:
        raise KeyError(f"Réponse CoinGecko invalide : {data}")
    return data["bitcoin"]["usd"], data["ethereum"]["usd"]

# === Script principal ===
def main():
    paliers = {
        "BTC": [130000, 150000, 180000, 200000],
        "ETH": [6400, 8000, 10000, 12000]
    }

    # 1️⃣ Récupération RSI
    try:
        rsi_data = get_bulk_rsi()
        rsi_btc = rsi_data[0]["result"]["value"]
        rsi_eth = rsi_data[1]["result"]["value"]
    except Exception as e:
        send_telegram(f"❌ Erreur récupération RSI : {e}")
        return

    # 2️⃣ Récupération prix
    try:
        prix_btc, prix_eth = get_prices()
    except Exception as e:
        send_telegram(f"❌ Erreur récupération prix : {e}")
        return

    # 3️⃣ Vérification paliers
    actifs = [
        ("BTC", prix_btc, rsi_btc),
        ("ETH", prix_eth, rsi_eth)
    ]

    for actif, prix, rsi in actifs:
        try:
            print(f"{actif} → Prix: {prix}$ | RSI: {rsi}")
            for palier in paliers[actif]:
                if prix >= palier:
                    send_telegram(f"🚀 {actif} a atteint {palier}$ (RSI: {rsi:.2f})")
        except Exception as e:
            send_telegram(f"❌ Erreur {actif} : {e}")

if __name__ == "__main__":
    main()

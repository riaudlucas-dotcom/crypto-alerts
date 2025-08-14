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
        else:
            print("✅ Message Telegram envoyé")
    except Exception as e:
        print(f"⚠️ Exception Telegram: {e}")

def get_prices(symbols):
    """Récupère les prix de plusieurs actifs depuis CoinGecko en un seul appel."""
    ids_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum"
    }
    ids_str = ",".join(ids_map[s] for s in symbols)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids_str}&vs_currencies=usd"
    data = requests.get(url, timeout=20).json()
    prices = {sym: data[ids_map[sym]]["usd"] for sym in symbols}
    return prices

def get_bulk_rsi(symbols, interval="1w"):
    """Récupère le RSI de plusieurs actifs via TAAPI.io en un seul appel."""
    url = f"https://api.taapi.io/bulk?secret={TAAPI_KEY}"
    indicators_payload = [
        {"indicator": "rsi", "exchange": "binance", "symbol": f"{sym}/USDT", "interval": interval}
        for sym in symbols
    ]
    payload = {"indicators": indicators_payload}

    r = requests.post(url, json=payload, timeout=20)
    data = r.json()

    if "errors" in data:
        raise ValueError(f"Erreur TAAPI.io: {data}")

    # TAAPI renvoie une liste de résultats dans "data"
    rsi_values = {}
    for result in data.get("data", []):
        symbol = result.get("result", {}).get("symbol", "")
        value = result.get("result", {}).get("value", None)
        if symbol and value is not None:
            rsi_values[symbol.replace("/USDT", "")] = value

    return rsi_values

# === Script principal ===
def main():
    actifs = ["BTC", "ETH"]
    paliers = {
        "BTC": [130000, 150000, 180000, 200000],
        "ETH": [6400, 8000, 10000, 12000]
    }

    try:
        prix_actuels = get_prices(actifs)
        rsi_actuels = get_bulk_rsi(actifs)

        for actif in actifs:
            prix = prix_actuels.get(actif)
            rsi = rsi_actuels.get(actif)

            print(f"{actif} → Prix: {prix}$ | RSI: {rsi}")

            if prix is None or rsi is None:
                send_telegram(f"⚠️ Données manquantes pour {actif}")
                continue

            for palier in paliers[actif]:
                if prix >= palier:
                    send_telegram(f"🚀 {actif} a atteint {palier}$ (RSI: {rsi:.2f})")

    except Exception as e:
        send_telegram(f"❌ Erreur récupération données : {e}")
        print(f"Erreur : {e}")

if __name__ == "__main__":
    main()

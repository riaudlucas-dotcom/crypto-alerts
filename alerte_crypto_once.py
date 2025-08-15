import os
import requests
import sys

# === Récupération des secrets GitHub ===
TAAPI_KEY = os.getenv("TAAPI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Vérification des variables
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
    """Récupère les prix USD de plusieurs cryptos en un seul appel CoinGecko."""
    ids_map = {"BTC": "bitcoin", "ETH": "ethereum"}
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={','.join(ids_map[s] for s in symbols)}&vs_currencies=usd"
    data = requests.get(url, timeout=20).json()
    prices = {}
    for sym in symbols:
        coin_id = ids_map[sym]
        if coin_id in data and "usd" in data[coin_id]:
            prices[sym] = data[coin_id]["usd"]
        else:
            print(f"⚠️ Données manquantes pour {sym}")
    return prices

def get_bulk_rsi(symbols, interval="1w"):
    """Récupère le RSI de plusieurs cryptos via TAAPI.io en un seul appel."""
    url = f"https://api.taapi.io/bulk?secret={TAAPI_KEY}"
    indicators_payload = [
        {"indicator": "rsi", "exchange": "binance", "symbol": f"{sym}/USDT", "interval": interval}
        for sym in symbols
    ]
    payload = {"indicators": indicators_payload}

    r = requests.post(url, json=payload, timeout=20)
    data = r.json()

    # 🔍 Debug : voir la réponse brute
    print("Réponse brute TAAPI.io :", data)

    if "errors" in data:
        print(f"⚠️ Erreur TAAPI.io: {data}")
        return {}

    rsi_values = {}
    for result in data.get("data", []):
        # On ne connaît pas encore la clé exacte, donc on teste plusieurs options
        symbol = result.get("symbol") or result.get("input", {}).get("symbol", "")
        value = result.get("result", {}).get("value")
        if symbol and value is not None:
            rsi_values[symbol.replace("/USDT", "").upper()] = value

    return rsi_values

# === Script principal ===
def main():
    actifs = ["BTC", "ETH"]
    paliers = {
        "BTC": [130000, 150000, 180000, 200000],
        "ETH": [6400, 8000, 10000, 12000]
    }

    try:
        prix_actuels = get_bulk_prices(actifs)
        rsi_actuels = get_bulk_rsi(actifs)

        for actif in actifs:
            prix = prix_actuels.get(actif)
            rsi = rsi_actuels.get(actif, None)

            if prix is None:
                continue  # pas de prix = on saute

            print(f"{actif} → Prix: {prix}$ | RSI: {rsi if rsi else 'N/A'}")

            for palier in paliers[actif]:
                if prix >= palier:
                    if rsi is not None:
                        send_telegram(f"🚀 {actif} a atteint {palier}$ (RSI: {rsi:.2f})")
                    else:
                        send_telegram(f"🚀 {actif} a atteint {palier}$ (RSI indisponible)")

    except Exception as e:
        send_telegram(f"❌ Erreur script : {e}")
        print(f"Erreur script : {e}")

if __name__ == "__main__":
    main()

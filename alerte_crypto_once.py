import os
import requests
import sys
import time

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

def get_price(symbol: str) -> float:
    """Récupère le prix en USD depuis CoinGecko."""
    ids = {"BTC": "bitcoin", "ETH": "ethereum"}
    symbol = symbol.upper()
    if symbol not in ids:
        raise ValueError(f"Symbole non supporté: {symbol}")
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids[symbol]}&vs_currencies=usd"
    data = requests.get(url, timeout=20).json()
    if ids[symbol] not in data or "usd" not in data[ids[symbol]]:
        raise KeyError(f"Clé '{ids[symbol]}' introuvable dans la réponse API : {data}")
    return data[ids[symbol]]["usd"]

# === Nouvelle fonction RSI groupé avec cache ===
RSI_CACHE = {}
CACHE_DURATION = 900  # 15 minutes

def get_rsi_bulk(symbols, interval="1h"):
    """Récupère le RSI pour plusieurs symboles en une seule requête."""
    now = time.time()
    result = {}
    need_call = any(sym not in RSI_CACHE or now - RSI_CACHE[sym]["time"] > CACHE_DURATION for sym in symbols)
    
    if not need_call:
        for sym in symbols:
            result[sym] = RSI_CACHE[sym]["rsi"]
        return result

    # Requête groupée TAAPI.io
    url = "https://api.taapi.io/bulk"
    params = {
        "secret": TAAPI_KEY,
        "symbols": ",".join([f"{sym.upper()}/USDT" for sym in symbols]),
        "indicators": "rsi",
        "interval": interval,
        "exchange": "binance"
    }
    try:
        data = requests.get(url, params=params, timeout=20).json()
        for sym in symbols:
            key = f"{sym.upper()}/USDT"
            rsi_value = data.get(key, {}).get("rsi", None)
            if rsi_value is not None:
                RSI_CACHE[sym] = {"rsi": rsi_value, "time": now}
                result[sym] = rsi_value
            else:
                result[sym] = f"Erreur TAAPI.io: {data.get(key, 'Pas de données')}"
    except Exception as e:
        for sym in symbols:
            result[sym] = f"Erreur TAAPI.io: {e}"
    return result

# === Script principal ===
def main():
    actifs = ["BTC", "ETH"]
    paliers = {
        "BTC": [130000, 150000, 180000, 200000],
        "ETH": [6400, 8000, 10000, 12000]
    }

    try:
        prices = {sym: get_price(sym) for sym in actifs}
        rsis = get_rsi_bulk(actifs)
    except Exception as e:
        send_telegram(f"❌ Erreur récupération prix/RSI: {e}")
        return

    for actif in actifs:
        prix = prices[actif]
        rsi = rsis[actif]
        print(f"{actif} → Prix: {prix}$ | RSI: {rsi}")
        for palier in paliers[actif]:
            if prix >= palier:
                send_telegram(f"🚀 {actif} a atteint {palier}$ (RSI: {rsi})")

if __name__ == "__main__":
    main()

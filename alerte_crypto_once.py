import os
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TAAPI_KEY = os.getenv("TAAPI_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

PALIERS = [
    ("BTC", 130000, 20),
    ("BTC", 150000, 20),
    ("BTC", 180000, 25),
    ("BTC", 200000, 15),
    ("ETH", 8000, 20),
    ("ETH", 10000, 20),
    ("ETH", 12000, 25),
    ("ETH", 14000, 15),
]

def get_price(symbol):
    ids = {"BTC": "bitcoin", "ETH": "ethereum"}
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids[symbol]}&vs_currencies=usd"
    return requests.get(url, timeout=20).json()[ids[symbol]]["usd"]

def get_rsi(symbol):
    if not TAAPI_KEY:
        return None
    pair = f"{symbol}/USDT"
    url = f"https://api.taapi.io/rsi?secret={TAAPI_KEY}&exchange=binance&symbol={pair}&interval=1w"
    try:
        return requests.get(url, timeout=20).json().get("value")
    except Exception:
        return None

def get_fear_greed():
    try:
        url = "https://api.alternative.me/fng/?limit=1&format=json"
        return int(requests.get(url, timeout=20).json()["data"][0]["value"])
    except Exception:
        return None

def send_telegram(message):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Telegram non configuré.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    requests.post(url, data=payload, timeout=20)

def main():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    fear_greed = get_fear_greed()
    lines = [f"=== Vérification {now} ===", f"Fear & Greed: {fear_greed}"]
    alerts = []
    for actif, palier, pct in PALIERS:
        prix = get_price(actif)
        rsi = get_rsi(actif)
        lines.append(f"{actif}: {prix}$ | RSI: {rsi}")
        if (prix and prix >= palier) or (rsi and rsi > 90) or (fear_greed is not None and fear_greed >= 90):
            alerts.append(f"🚨 Signal VENTE {actif} !\nPrix: {prix}$\nRSI: {rsi}\nFear&Greed: {fear_greed}\nPalier: {palier}$ ({pct}%)")
    print("\n".join(lines))
    for a in alerts:
        print(a)
        send_telegram(a)

if __name__ == "__main__":
    main()

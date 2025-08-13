import os
import requests
import sys

# Récupération des secrets GitHub Actions
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Vérification des variables essentielles
missing = [var for var, value in {
    "TELEGRAM_TOKEN": TELEGRAM_TOKEN,
    "CHAT_ID": CHAT_ID
}.items() if not value]

if missing:
    print(f"❌ Secrets manquants : {', '.join(missing)}")
    sys.exit(1)

def send_telegram(message: str):
    """Envoie un message Telegram via Bot API."""
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": message}
        r = requests.post(url, data=payload, timeout=10)
        if r.status_code != 200:
            print(f"⚠️ Erreur envoi Telegram: {r.text}")
        else:
            print("✅ Message Telegram envoyé avec succès !")
    except Exception as e:
        print(f"⚠️ Exception Telegram: {e}")

if __name__ == "__main__":
    send_telegram("✅ Test Telegram réussi : le bot fonctionne et le chat est correct !")

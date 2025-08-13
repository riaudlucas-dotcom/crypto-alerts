# Crypto Alerts Pack (BTC & ETH)

Deux façons gratuites de faire tourner les alertes :

## Option A — GitHub Actions (recommandé, 100% gratuit)
- Le workflow `.github/workflows/alerts.yml` exécute `alerte_crypto_once.py` **toutes les heures**.
- Configure tes **Secrets** dans GitHub : `TAAPI_KEY`, `TELEGRAM_TOKEN`, `CHAT_ID`.

## Option B — Render (service gratuit, peut s'endormir)
- Déploie ce repo sur Render (plan *Free*). 
- Le service lance `alerte_crypto_loop.py` en continu (tant que l'instance est éveillée).
- Ajoute tes variables d'environnement dans Render Dashboard.

## Variables .env
```
TAAPI_KEY=TA_CLE_API
TELEGRAM_TOKEN=TON_TOKEN_BOT
CHAT_ID=TON_CHAT_ID
INTERVALLE=3600
```

## PALIERS
Modifie la liste dans `alerte_crypto_once.py` si besoin.

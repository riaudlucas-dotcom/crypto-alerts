import os
import time
from dotenv import load_dotenv
from alerte_crypto_once import main as run_once

load_dotenv()
INTERVALLE = int(os.getenv("INTERVALLE", "3600"))

if __name__ == "__main__":
    while True:
        try:
            run_once()
        except Exception as e:
            print("Erreur:", e)
        time.sleep(INTERVALLE)

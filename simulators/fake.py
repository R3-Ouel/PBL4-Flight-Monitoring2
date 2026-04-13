import time         # Pour le timestamp et les pauses
import os           # Pour la gestion du fichier CSV
import csv          # Pour l'écriture locale
import math         # Pour simuler des courbes fluides (sinus/cosinus)
import random       # Pour ajouter un peu de "bruit" réaliste aux données
import requests

# --- 1. CONFIGURATION ---
BACKEND_ENDPOINT = "http://127.0.0.1:8000/push"

# CSV dans le même dossier que ce script
HERE = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(HERE, "log_simulation.csv")
HEADERS = [
    "timestamp", "altitude", "vitesse", "ax", "ay", "az",
    "roll", "pitch", "yaw", "temperature", "pression",
    "latitude", "longitude", "batterie", "phase"
]

if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        csv.writer(f).writerow(HEADERS)


def run_simulation():
    print("🎮 Fake simulator démarré — envoi vers backend %s" % BACKEND_ENDPOINT)

    start_time = time.time()
    alt = 0.0
    vitesse = 0.0
    batterie = 100.0
    lat = 48.8584  # Coordonnées de départ (Paris par exemple)
    lon = 2.2945

    session = requests.Session()

    while True:
        elapsed = time.time() - start_time

        # Phases
        if elapsed < 10 and alt < 15:
            phase = "DECOLLAGE"
            alt += 0.5 + random.uniform(-0.1, 0.1)
            vitesse = 2.0 + random.uniform(0, 0.5)
        elif elapsed < 40:
            phase = "VOL_STABILISE"
            alt = 15.0 + math.sin(elapsed) * 0.5
            vitesse = 5.0 + random.uniform(-0.2, 0.2)
            lon += 0.0001
        else:
            phase = "ATTERRISSAGE"
            alt -= 0.3
            vitesse = 1.0
            if alt <= 0:
                alt = 0
                phase = "TERMINE"

        # Orientation
        roll = math.sin(elapsed * 0.5) * 5.0
        pitch = math.cos(elapsed * 0.5) * 3.0
        yaw = (elapsed * 2) % 360

        # Batterie et températures
        batterie = max(0.0, batterie - 0.05)
        temp = 25.0 + (math.sin(elapsed * 0.1) * 2.0)

        # Préparer payload conforme au backend
        payload = {
            "flight_id": "FAKE_SIM",
            "timestamp_ms": int(time.time() * 1000),
            "altitude": round(alt, 2),
            "vitesse": round(vitesse, 2),
            "ax": round(random.uniform(-0.5, 0.5), 3),
            "ay": round(random.uniform(-0.5, 0.5), 3),
            "az": round(9.81 + random.uniform(-0.1, 0.1), 3),
            "roll": round(roll, 2),
            "pitch": round(pitch, 2),
            "yaw": round(yaw, 2),
            "phase": phase,
            # Nouveaux champs demandés
            "batterie": round(batterie, 1),
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            # gardons quelques champs utiles
            "temperature": round(temp, 2),
            "pression": round(1013.25 - (alt * 0.12), 2)
        }
        
        # Envoi au backend
        try:
            resp = session.post(BACKEND_ENDPOINT, json=payload, timeout=1)
            if resp.status_code != 200:
                print(f"[WARN] backend returned {resp.status_code}")
        except Exception as e:
            # Ne pas planter si backend indisponible
            print("[WARN] failed to POST to backend:", e)

        # Fréquence d'émission
        time.sleep(0.2)

        if phase == "TERMINE":
            print("🏁 Simulation finie.")
            break


if __name__ == "__main__":
    run_simulation()
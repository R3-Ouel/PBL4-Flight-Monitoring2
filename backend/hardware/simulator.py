import csv
import time
import os
import random
import requests
from dotenv import load_dotenv
from supabase import create_client

# ================= CONFIG =================
DURATION = 120
TIME_STEP = 1
TARGET_ALTITUDE = 10  # altitude cible
ASCENT_DURATION = random.randint(5, 10)  # montée en 5 à 10 secondes

# ================= SUPABASE =================
load_dotenv()
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase = create_client(url, key)

# s = Client(url, key)

# ================= SIMULATION =================
def simulate_and_send():
    data_csv = []

    altitude = 0
    vitesse = 0
    flight_id = "VOL_NEON_FUSION_02"

    print(f"Montée vers {TARGET_ALTITUDE}m en {ASCENT_DURATION}s")

    for t in range(0, DURATION, TIME_STEP):

        # ===== PHASES =====
        if t < ASCENT_DURATION:
            phase = "Montée"
            # progression douce vers 10m
            altitude += TARGET_ALTITUDE / ASCENT_DURATION + random.uniform(-0.2, 0.2)
            vitesse += random.uniform(0.5, 1.0)

        elif t < 80:
            phase = "Stabilisation"
            altitude += random.uniform(-0.2, 0.2)
            vitesse += random.uniform(-0.2, 0.2)

        else:
            phase = "Descente"
            altitude -= random.uniform(0.5, 1.0)
            vitesse -= random.uniform(0.3, 0.7)

        # Sécurité
        altitude = max(0, altitude)
        vitesse = max(0, vitesse)

        # ===== ACCELERATION =====
        ax = random.uniform(-0.5, 0.5)
        ay = random.uniform(-0.5, 0.5)
        az = round(9.81 + random.uniform(-0.3, 0.3), 2)

        # ===== ORIENTATION =====
        roll = random.uniform(-5, 5)
        pitch = 5 if phase == "Montée" else -5 if phase == "Descente" else 0
        yaw = (t * 3) % 360

        # ===== FORMAT DATA =====
        row = [
            t,
            round(altitude, 2),
            round(vitesse, 2),
            round(ax, 2),
            round(ay, 2),
            az,
            round(roll, 2),
            round(pitch, 2),
            round(yaw, 2),
        ]

        data_csv.append(row)

        data_supabase = {
            "flight_id": flight_id,
            "timestamp_ms": t * 1000,
            "altitude": round(altitude, 2),
            "vitesse": round(vitesse, 2),
            "ax": round(ax, 2),
            "ay": round(ay, 2),
            "az": az,
            "roll": round(roll, 2),
            "pitch": round(pitch, 2),
            "yaw": round(yaw, 2),
            "phase": phase
        }

        # ===== ENVOI SUPABASE =====
        try:
            supabase.table("telemetrie").insert(data_supabase).execute()
        except Exception as e:
            print("Erreur Supabase:", e)

        # ===== ENVOI AU BACKEND LOCAL (broadcast WebSocket via /push) =====
        try:
            requests.post("http://127.0.0.1:8000/push", json=data_supabase, timeout=0.5)
        except Exception as e:
            # Ne pas bloquer la simulation si le backend n'est pas disponible
            pass

        print(f"{t}s | {phase} | Alt: {altitude:.2f} m")

        time.sleep(0.01)  # Simule un délai de 10ms

    return data_csv


# ================= CSV =================
def save_to_csv(data, filename="flight_data.csv"):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)

        writer.writerow([
            "timestamp",
            "altitude",
            "vitesse",
            "ax",
            "ay",
            "az",
            "roll",
            "pitch",
            "yaw"
        ])

        writer.writerows(data)


# ================= MAIN =================
if __name__ == "__main__":
    data = simulate_and_send()
    save_to_csv(data)
    print("Simulation + Supabase + CSV terminés 🚀")
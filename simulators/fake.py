import time
import random
import requests

# ================= CONFIG =================
DURATION = 120
TIME_STEP = 1
TARGET_ALTITUDE = 10  # altitude cible
ASCENT_DURATION = random.randint(5, 10)  # montée en 5 à 10 secondes

# Endpoint du backend local (port 8000)
BACKEND_ENDPOINT = "http://127.0.0.1:8000/push"


# ================= SIMULATION =================
def simulate_and_send():
    altitude = 0
    vitesse = 0
    flight_id = "VOL_NEON_FUSION_02"

    print(f"Montée vers {TARGET_ALTITUDE}m en {ASCENT_DURATION}s")

    roll = 0.0
    pitch = 0.0
    yaw = random.uniform(0, 360)

    for t in range(0, DURATION, TIME_STEP):
        # Phases
        if t < ASCENT_DURATION:
            phase = "Montée"
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

        altitude = max(0, altitude)
        vitesse = max(0, vitesse)

        ax = random.uniform(-0.5, 0.5)
        ay = random.uniform(-0.5, 0.5)
        az = round(9.81 + random.uniform(-0.3, 0.3), 2)

        roll = random.uniform(-5, 5)
        pitch = 5 if phase == "Montée" else -5 if phase == "Descente" else 0
        yaw = (t * 3) % 360

        payload = {
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
            "phase": phase,
        }

        # Envoi uniquement vers le backend local (POST /push)
        try:
            requests.post(BACKEND_ENDPOINT, json=payload, timeout=0.5)
        except Exception:
            # Ne pas bloquer la simulation si le backend n'est pas disponible
            pass

        print(f"{t}s | {phase} | Alt: {altitude:.2f} m")
        time.sleep(0.5)


if __name__ == "__main__":
    simulate_and_send()
    print("Simulation terminée — envoi vers backend uniquement 🚀")
import asyncio      # Pour gérer les tâches asynchrones (WebSocket Flutter)
import websockets   # Pour la communication temps réel avec l'interface
import json         # Pour formater les messages en JSON
import time         # Pour les calculs de temps et pauses
import os           # Pour la gestion des fichiers (vérifier si le CSV existe)
import csv          # Pour lire et écrire dans le fichier tableur
import threading    # Pour gérer la synchronisation Cloud en tâche de fond
from supabase import create_client # Pour envoyer les données sur Supabase
from pymavlink import mavutil      # Pour décoder les données du Pixhawk

# --- 1. CONFIGURATION ---
sup_url = "TON_URL_SUPABASE" # url de la base de données Supabase 
sup_key = "TA_CLE_API_SUPABASE" # la clé API de Supabase
supabase = create_client(sup_url, sup_key)# c'est le pont entre nous et superbase, on l'utilisera pour envoyer les données

#Création du fichier CSV local pour stocker les données de vol 
CSV_FILE = "flight_data.csv"
# Liste officielle des colonnes (doit correspondre à ta table Supabase) # Juan faut modifier 
HEADERS = [
    "timestamp", "altitude", "vitesse", "ax", "ay", "az", 
    "roll", "pitch", "yaw", "temperature", "pression", 
    "longitude", "latitude", "batterie", "phase"
]

# Initialisation du CSV : on crée l'en-tête s'il n'existe pas encore
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, 'w', newline='') as f:
        csv.writer(f).writerow(HEADERS)

# --- 2. LOGIQUE DE DÉTECTION DES PHASES ---
def detect_phase(alt, vitesse): #JUAN modifie l'altitude et la vitesse pour les seuils de détection
    if alt < 1.0 and vitesse < 0.5:
        return "Au sol"
    elif alt > 2.0 and vitesse > 1.5:
        return "Decollage / Vol"
    elif alt < 2.0 and vitesse < 1.0:
        return "Atterrissage"
    return "Stabilisation"

# --- 3. SYNCHRONISATION INTELLIGENTE (Rattrapage Missions Offline) ---
def smart_sync_cloud():
    """Lit le CSV et envoie les données non encore présentes sur le Cloud"""
    last_sent_row = 0 # Curseur pour savoir où on s'est arrêté de lire
    
    while True:
        if os.path.exists(CSV_FILE):
            try:
                with open(CSV_FILE, 'r') as f:
                    # On transforme le CSV en liste de dictionnaires
                    all_data = list(csv.DictReader(f))
                    total_rows = len(all_data)

                    # Si le fichier contient plus de lignes que ce qu'on a envoyé
                    if total_rows > last_sent_row:
                        # On prend un paquet de 50 lignes maximum à la fois
                        batch = all_data[last_sent_row : last_sent_row + 50]
                        
                        # Envoi à la table "telemetry" de Supabase
                        supabase.table("telemetry").insert(batch).execute()
                        
                        # Si l'envoi réussit, on avance notre curseur
                        last_sent_row += len(batch)
                        print(f" Sync Cloud : +{len(batch)} lignes (Total envoyé: {last_sent_row})")
                
                time.sleep(1) # Vérification rapide si connexion OK
            except Exception as e:
                # Si échec (pas d'internet), on attend plus longtemps avant de réessayer
                print(" Mode Offline : En attente de connexion pour synchroniser...")
                time.sleep(10) 
        else:
            time.sleep(5)

# Lancer la synchronisation intelligente dans un fil (thread) séparé
threading.Thread(target=smart_sync_cloud, daemon=True).start()

# --- 4. RÉCUPÉRATION DRONE ET ENVOI FLUTTER ---
async def handle_telemetry(websocket, path):
    # Connexion au drone via UDP (Port standard 14550)
    mav = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
    
    # Dictionnaire pour stocker l'état actuel (Fusion des messages MAVLink)
    state = {k: 0 for k in HEADERS}
    state["phase"] = "Initialisation"
    motors_armed = False

    print(" Serveur prêt. En attente de données du drone...")

    while True:
        # On intercepte les messages vitaux du drone
        msg = mav.recv_match(type=['GLOBAL_POSITION_INT', 'ATTITUDE', 'SYS_STATUS', 
                                   'RAW_IMU', 'VFR_HUD', 'SCALED_PRESSURE', 'HEARTBEAT'], 
                             blocking=True)
        
        if msg:
            m_type = msg.get_type()
            state["timestamp"] = int(time.time()) # Heure Unix (secondes)

            # A. Détection arrêt automatique (HEARTBEAT)
            if m_type == 'HEARTBEAT':
                was_armed = motors_armed
                # Vérifie si les moteurs sont activés
                motors_armed = (msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
                
                # Si moteurs coupés au sol après avoir été armés = Fin de mission
                if was_armed and not motors_armed and state["altitude"] < 0.5:
                    state["phase"] = "Terminé"
                    print(" Mission finie. Arrêt du script.")
                    await websocket.send(json.dumps(state))
                    time.sleep(5) # Laisse le temps au thread Cloud de finir l'envoi
                    os._exit(0)

            # B. Conversion des données brutes en unités physiques
            elif m_type == 'GLOBAL_POSITION_INT':
                state["latitude"], state["longitude"] = msg.lat / 1e7, msg.lon / 1e7
                state["altitude"] = msg.relative_alt / 1000.0 # Mètres
            
            elif m_type == 'ATTITUDE':
                # Conversion Radians -> Degrés
                state["roll"] = msg.roll * (180 / 3.14159)
                state["pitch"] = msg.pitch * (180 / 3.14159)
                state["yaw"] = msg.yaw * (180 / 3.14159)
            
            elif m_type == 'RAW_IMU':
                # Conversion brute -> m/s²
                state["ax"], state["ay"], state["az"] = (msg.xacc/1000)*9.81, (msg.yacc/1000)*9.81, (msg.zacc/1000)*9.81
            
            elif m_type == 'VFR_HUD':
                state["vitesse"] = msg.groundspeed # m/s
            
            elif m_type == 'SCALED_PRESSURE':
                state["pression"] = msg.press_abs # hPa
                state["temperature"] = msg.temperature / 100.0 # °C
            
            elif m_type == 'SYS_STATUS':
                state["batterie"] = msg.battery_remaining # %

            # Mise à jour de la phase
            state["phase"] = detect_phase(state["altitude"], state["vitesse"]) if motors_armed else "Au sol"

            # C. SAUVEGARDE LOCALE (CSV) - C'est ici que les données sont figées
            with open(CSV_FILE, 'a', newline='') as f:
                csv.DictWriter(f, fieldnames=HEADERS).writerow(state)

            # D. ENVOI FLUTTER (JSON) - Pour l'affichage direct
            await websocket.send(json.dumps(state))

# --- 5. DÉMARRAGE DU SERVEUR ---
start_server = websockets.serve(handle_telemetry, "0.0.0.0", 8765)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
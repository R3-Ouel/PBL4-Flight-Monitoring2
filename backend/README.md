# Backend — FastAPI

Ce dossier contient le serveur HTTP qui reçoit la télémétrie et la diffuse aux clients via WebSocket.

Principaux fichiers

- `main.py` : serveur FastAPI
  - Endpoint HTTP `POST /push` : reçoit un paquet JSON de télémétrie et le diffuse aux clients WebSocket.
  - WebSocket `GET /ws/flight-data` : les frontends se connectent pour recevoir la télémétrie en direct.
  - Démarre un pusher de CSV en tâche de fond (voir `backend/core/manager.py`).

- `core/manager.py` : gestion de l'écriture CSV et (optionnel) push vers Supabase.
  - Écrit chaque payload dans `backend/data/flight_data.csv`.
  - Si `SUPABASE_URL` et `SUPABASE_KEY` sont fournis, envoie périodiquement des batches vers Supabase.
  - Le pusher applique une sanitation des champs pour éviter des erreurs de type (ex: bigint vs float).

## Installation

1. Créez et activez un environnement virtuel (recommandé) :

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

2. (Optionnel) Créez un fichier `.env` à la racine du projet et ajoutez vos identifiants Supabase :

```env
SUPABASE_URL=https://xyz.supabase.co
SUPABASE_KEY=eyJ...votre_cle...
```

Si Supabase n'est pas configuré, le backend continuera d'écrire dans le CSV local (`backend/data/flight_data.csv`).

## Exécution

- Lancement rapide (Windows) : `..\scripts\run_backend.bat` depuis la racine du projet.
- Ou depuis le dossier `backend/` :

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

## Endpoints & format

- POST `/push` (JSON) — attend un objet contenant au moins un `timestamp_ms` ou des champs mesurés.
- WebSocket `ws://127.0.0.1:8000/ws/flight-data` — diffuse chaque payload reçu.

Champs courants envoyés par les simulateurs :

```
flight_id, timestamp_ms, altitude, vitesse, ax, ay, az, roll, pitch, yaw, latitude, longitude, batterie, phase
```

Le fichier CSV utilisé localement est `backend/data/flight_data.csv`.

## Notes & dépannage

- Si vous voyez une erreur Supabase du type "invalid input syntax for type bigint", le pusher contient une logique pour forcer la conversion en types compatibles et désactiver des colonnes problématiques.
- Les logs du backend impriment des messages utiles en cas d'échec d'insertion; consultez la console lors d'exécution.

Pour plus de détails, lisez `backend/core/manager.py`.

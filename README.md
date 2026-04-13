# PBL 4 — Monitoring de télémétrie de vol (Go Phase)

Ce dépôt contient le code source développé pour la phase "Go" du projet PBL 4. Il permet de générer (simulateurs), collecter (backend) et visualiser (frontend) des données de télémétrie d'un vol réel ou simulé.

Principaux dossiers :

- `backend/` : serveur FastAPI qui reçoit la télémétrie, l'écrit en CSV et la pousse vers Supabase (optionnel).
- `frontend/` : application Flutter affichant le tableau de bord et consommant les données via WebSocket.
- `simulators/` : simulateurs (fake, mission_planner) qui postent des paquets JSON vers le backend.
- `scripts/` : scripts utilitaires pour démarrer les simulateurs et le backend sous Windows.

## Démarrage rapide

Prérequis :

- Python 3.8+ (idéalement 3.9), `pip` et `virtualenv` pour `backend/` et `simulators/`.
- Flutter SDK pour l'application `frontend/` (voir https://docs.flutter.dev/get-started/install).

Étapes minimales :

1. Installer les dépendances backend :

   Windows (depuis la racine du projet) :

   ```powershell
   cd backend
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Installer les dépendances des simulateurs :

   ```powershell
   cd simulators
   python -m venv venv
   .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. (Frontend) Récupérer les packages Flutter :

   ```bash
   cd frontend
   flutter pub get
   flutter run
   ```

4. Configurer Supabase (optionnel) : créer `.env` à la racine et définir `SUPABASE_URL` et `SUPABASE_KEY`.

5. Lancer le backend :

   - Windows : `scripts\run_backend.bat` (ouvre le serveur et démarre le pusher CSV en tâche de fond)
   - Ou depuis `backend/` : `uvicorn main:app --reload --host 127.0.0.1 --port 8000`

6. Lancer un simulateur :

   - Utilisez `scripts\run_simulators.bat` et choisissez `1` (Fake) ou `2` (Mission Planner) ou `3` (Both),
     ou lancez directement `python simulators\mission_planner.py`.

## Points d'intégration

- Endpoint HTTP pour recevoir la télémétrie : `POST http://127.0.0.1:8000/push`
- WebSocket (diffusion vers frontend) : `ws://127.0.0.1:8000/ws/flight-data`
- Fichier CSV local : `backend/data/flight_data.csv` (écriture par le backend)
- Si Supabase est configuré, les lignes CSV sont poussées vers la table `telemetrie`.

Champs JSON attendus (exemples) :

```json
{
  "flight_id": "SITL_MISSION",
  "timestamp_ms": 1670000000000,
  "altitude": 12.3,
  "vitesse": 4.2,
  "ax": 0.12,
  "ay": -0.03,
  "az": 0.01,
  "roll": 1.2,
  "pitch": 0.5,
  "yaw": 90,
  "latitude": 12.3456,
  "longitude": 56.7890,
  "batterie": 87,
  "phase": "GUIDED"
}
```

## Documentation détaillée

- Backend : [backend/README.md](backend/README.md)
- Frontend : [frontend/README.md](frontend/README.md)
- Simulateurs : [simulators/README.md](simulators/README.md)
- Scripts utilitaires : [scripts/README.md](scripts/README.md)

Si vous avez besoin d'aide pour exécuter le projet sur votre machine, dites-moi quel OS et je vous fournis les commandes pas-à-pas.

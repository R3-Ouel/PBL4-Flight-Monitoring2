Backend - structure et responsabilités
===================================

Fichiers et responsabilités :

- `main.py` : serveur FastAPI
  - Endpoint POST `/push` : reçoit des paquets de télémétrie JSON et les diffuse
    aux clients WebSocket.
  - WebSocket `/ws` : clients (frontend) se connectent pour recevoir les données en direct.
  - Ne pas générer de données dans ce fichier.

- `hardware/simulator.py` : simulation / génération de données
  - Génère des paquets de télémétrie et POSTe vers `http://127.0.0.1:8000/push`.
  - Peut aussi sauvegarder en CSV et envoyer vers Supabase si configuré.

Exécution (développement)
-------------------------
1) Installer dépendances (virtualenv ou conda) puis :

   pip install -r requirements.txt

2) Lancer le backend et le simulateur (fourni `run_backend.bat` pour Windows) :

   run_backend.bat

Notes
-----
- Pour la production, exécutez `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4` derrière
  un reverse-proxy.
- Si vous préférez que le simulateur envoie directement sur WebSocket, on peut le modifier
  pour ouvrir une connexion WebSocket au lieu de poster sur `/push`.

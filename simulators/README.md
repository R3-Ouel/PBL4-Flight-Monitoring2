# Simulateurs

Ce dossier contient des simulateurs qui génèrent de la télémétrie et la postent vers le backend (`POST /push`).

Fichiers importants :

- `fake.py` : simulateur simple, autonome, envoie des paquets JSON vers `http://127.0.0.1:8000/push`.
- `mission_planner.py` : lance un SITL (dronekit-sitl), exécute une mission automatique et poste la télémétrie MAVLink.
- `requirements.txt` : dépendances Python pour les simulateurs.

## Installation

Recommandé : créer et activer un virtualenv avant d'installer les dépendances :

```powershell
cd simulators
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Exécution

- Fake simulator :

  ```powershell
  python simulators\fake.py
  ```

  Envoie régulièrement des paquets JSON (contient `ax`, `ay`, `az`, `altitude`, `vitesse`, `batterie`, `latitude`, `longitude`, `phase`, ...).

- Mission Planner (SITL) :

  ```powershell
  python simulators\mission_planner.py
  # ou pour se connecter à un autopilot externe :
  python simulators\mission_planner.py connect
  ```

  Le script démarre SITL (téléchargera SITL si nécessaire), exécute une mission et poste la télémétrie vers `http://127.0.0.1:8000/push`. Il attend que l'atterrissage soit détecté (altitude faible + désarmé) avant de s'arrêter.

## Champs de télémétrie (extraits)

- `flight_id`, `timestamp_ms`, `altitude`, `vitesse`, `ax`, `ay`, `az`, `roll`, `pitch`, `yaw`, `latitude`, `longitude`, `batterie`, `phase`

Note : `mission_planner.py` lit `raw_imu` pour `ax/ay/az` quand disponible et calcule une estimation de `az` si nécessaire.

## Utilisation via les scripts

Pour un démarrage facilité sur Windows, utilisez `scripts\run_simulators.bat` (choix interactif). Ce script ouvre chaque simulateur dans une nouvelle fenêtre `cmd` et utilise `cmd /k` pour laisser la fenêtre ouverte.

Si vous avez des questions sur l'installation de DroneKit/SITL, dites-moi votre OS et je fournis les commandes exactes.

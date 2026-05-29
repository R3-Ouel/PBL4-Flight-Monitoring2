# Scripts utilitaires (Windows)

Ce dossier contient des scripts batch/PowerShell conçus pour faciliter le lancement des composants (backend, simulateurs, etc.) sous Windows.

Fichiers importants :

- `run_simulators.bat` : menu interactif pour démarrer `simulators\fake.py` et/ou `simulators\mission_planner.py` dans des fenêtres séparées (`cmd /k` pour garder la fenêtre ouverte).
- `run_backend.bat` : démarre le backend (FastAPI) dans une fenêtre.
- `run_all.bat` : script utilitaire pour démarrer plusieurs composants en séquence (voir le contenu pour détails).
- `run_frontend_react.bat` : démarre le frontend React (Vite) dans `frontend-react/`.
- `run_all_react.bat` : démarre le frontend React puis le backend.
- `setup.bat` : script d'installation/initialisation (peut créer des environnements ou installer des dépendances selon projet).
- `kill_simulators.ps1` : utilitaire PowerShell pour tuer les processus de simulateur (optionnel). Note : l'appel automatique est désactivé dans `run_simulators.bat` pour éviter des problèmes d'interprétation.

Usage rapide

- Démarrer les simulateurs (menu interactif) : double-cliquez `run_simulators.bat` ou exécutez-le depuis PowerShell/CMD.
- Démarrer le backend : exécutez `run_backend.bat` depuis la racine du projet.

Notes

- `run_simulators.bat` tente d'activer un virtualenv présent dans `simulators/venv` (ou `backend/sim_venv`). Si aucun environnement n'est trouvé, il utilise le `python` système.
- Les fenêtres des simulateurs sont laissées ouvertes (`cmd /k`) pour permettre de lire les logs et voir d'éventuelles erreurs.
- Si vous voulez automatiser l'arrêt des simulateurs, vous pouvez exécuter `kill_simulators.ps1` manuellement (autorisation d'exécution PowerShell peut être nécessaire : `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`).

Si vous souhaitez que j'automatise un flux de démarrage personnalisé (par ex. lancement du backend + mission_planner + frontend), dites-moi le scénario et je peux adapter `run_all.bat` ou ajouter un script PowerShell dédié.

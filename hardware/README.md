# 📡 Module Hardware & Acquisition de Données

Bienvenue dans le module **Hardware** du projet de Mécanique du Vol !

L'objectif de ce dossier est de gérer l'**acquisition des données** de l'avion, qu'elles proviennent d'un modèle virtuel (simulation) ou de capteurs physiques embarqués. C'est ici que l'on transforme le monde physique (ou les lois de la physique) en données numériques compréhensibles par notre base de données.

## 📁 Que contient ce dossier ?

- **`simulator.py`** : Un script très utile pour générer un vol virtuel de toutes pièces ! Il calcule l'altitude, la vitesse, l'accélération sur 3 axes ($a_x, a_y, a_z$) et l'inclinaison (roll, pitch, yaw) au fil des différentes phases du vol (montée, stabilisation, virage, descente). **Idéal pour tester l'application quand on n'a pas accès au matériel.**
- **`serial_data.py`** : Ce script est prévu pour lire les données réelles issues d'un port série (par exemple depuis une carte Arduino, un ESP32 ou tout autre microcontrôleur relié à une centrale inertielle - IMU).

## 🛠️ Comment l'utiliser ?

### Lancer la Simulation
Pour voir comment l'application réagit ou remplir la base de données avec un faux vol de test :
```bash
# À exécuter depuis le dossier parent (02_Coding)
python hardware/simulator.py
```
Le simulateur se chargera d'envoyer les coordonnées télémétriques directement à **Supabase**.

### Connecter du vrai matériel
Si vous avez un capteur (ex: accéléromètre MPU6050) branché en USB :
1. Modifiez `serial_data.py` pour indiquer le bon port COM (sous Windows) ou `/dev/ttyUSB0` (sous Linux/Mac).
2. Programmez sa fréquence de lecture.
3. Exécutez le script pour injecter des vraies données en direct !

---
**💡 Astuce pour les collaborateurs :** 
Si vous modifiez la structure des données envoyées (par exemple pour rajouter la température), n'oubliez pas de prévenir les équipes s'occupant de `core/` et `ui/` !

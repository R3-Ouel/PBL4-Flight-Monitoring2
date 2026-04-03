# ✈️ PBL 4 : Mécanique du Vol - Système de Monitoring (Go Phase)

Bienvenue dans le dépôt principal du projet **PBL 4 : Mécanique du Vol** (Forces mises en jeu lors du déplacement d'un avion).

Ce dossier `02_Coding` contient l'ensemble du code source développé lors de la **Go Phase**. Il vise à acquérir, traiter, et visualiser les données de télémétrie d'un vol (réel ou simulé). L'objectif est de permettre à n'importe quel collaborateur ou curieux de comprendre les forces qui s'appliquent sur un avion en vol grâce à une interface de monitoring de données.

---

## 🏗️ Architecture du Projet

Le projet a été pensé de manière modulaire afin que chacun puisse travailler sur sa partie sans gêner les autres :

1. **[`hardware/`](./hardware/)** : Contient les scripts pour la récupération des données. Vous y trouverez un simulateur de vol (`simulator.py`) ainsi que le lien avec des capteurs physiques (`serial_data.py`).
2. **[`core/`](./core/)** : C'est le "cerveau" de l'application. On y gère la connexion à la base de données (Supabase) et les calculs analytiques (mathématiques du vol, traitement des données).
3. **[`ui/`](./ui/)** : L'interface utilisateur (Dashboard). C'est ici que l'on construit les tableaux de bord interactifs (avec Streamlit ou Flet) pour visualiser les données en temps réel.

---

## 🚀 Guide de Démarrage (Pour les collaborateurs)

Que vous soyez un développeur expérimenté ou un amateur curieux, voici comment lancer le projet chez vous :

### 1. Prérequis
Assurez-vous d'avoir [Python 3](https://www.python.org/downloads/) installé sur votre machine.

### 2. Installation des dépendances
Ouvrez un terminal dans ce dossier `02_Coding` et installez les bibliothèques nécessaires :
```bash
# S'il y a un environnement virtuel, activez-le d'abord (ex: venv\Scripts\activate sur Windows)
pip install -r requirements.txt
```

### 3. Configuration de la base de données (Supabase)
Pour que les scripts puissent communiquer avec la base de données :
1. Créez un fichier `.env` à la racine du dossier `02_Coding` (un modèle ou fichier vide s'y trouve peut-être déjà).
2. Ajoutez-y vos clés API Supabase :
   ```env
   SUPABASE_URL=votre_url_supabase
   SUPABASE_KEY=votre_cle_api_supabase
   ```

### 4. Lancer une simulation
Pour générer des données de vol virtuelles :
```bash
python hardware/simulator.py
```
*Le terminal vous affichera les informations envoyées (altitude, vitesse, inclinaison, etc.).*

### 5. Lancer l'interface utilisateur
Pour voir le tableau de bord (selon le framework que vous avez choisi d'utiliser) :
```bash
streamlit run ui/app_streamlit.py
# ou
python ui/app_flet.py
```

---

## 🤝 Comment Contribuer ?

- **Amateurs d'électronique** : Allez dans le dossier `hardware/` pour améliorer le code de récupération des capteurs Arduino/ESP32.
- **Mathématiciens et Data Scientists** : Allez dans le dossier `core/` pour injecter vos formules de mécanique du vol (portance, traînée, poids, poussée) dans `analytics.py`.
- **Designers & Développeurs Frontend** : Allez dans `ui/` pour rendre le tableau de bord encore plus lisible et agréable !

*(Pour plus de détails, n'hésitez pas à lire les `README.md` présents dans chaque sous-dossier.)*

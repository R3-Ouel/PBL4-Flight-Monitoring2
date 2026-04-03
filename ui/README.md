# 🎨 Module UI : Interface Utilisateur & Dashboard

Bienvenue dans le module **Interface Utilisateur (UI)** du projet **PBL 4 : Mécanique du vol**.

Ce dossier a pour but d'afficher à l'écran, de manière claire et visuelle, les milliers de données de vol reçues (venant de `hardware/`) et calculées (dans `core/`). Il s'agit du pont direct entre les mathématiques du vol et l'œil du pilote (ou de l'ingénieur) !

## 📁 Que contient ce dossier ?

Plutôt que d'imposer un seul style de développement, ce dossier propose un socle pour deux bibliothèques Python extrêmement populaires pour la création de dashboards de données :

- **`app_streamlit.py`** : L'interface construite avec Streamlit, souvent très rapide à mettre en place avec de beaux graphiques natifs, idéale pour afficher simplement des courbes (altitude, vitesse) en temps réel avec un rafraîchissement rapide.
- **`app_flet.py`** : L'interface construite avec Flet (basé sur le moteur Flutter de Google). Très puissant si vous souhaitez une interface plus proche d'une "vraie" application de bureau, avec des widgets très personnalisables.
- **`theme.py`** : Fichier pour paramétrer le design graphique global du projet.

## 🛠️ Comment lancer l'interface ?

Selon votre préférence (assurez-vous d'avoir installé `requirements.txt` à la racine), lancez la commande appropriée depuis le dossier "02_Coding" (et non depuis un sous-dossier) :

### Lancer Streamlit
```bash
streamlit run ui/app_streamlit.py
```
> Ceci ouvrira automatiquement votre navigateur web sur l'adresse locale `http://localhost:8501`.

### Lancer Flet
```bash
python ui/app_flet.py
```
> L'interface Flet apparaîtra soit sous la forme d'une application bureau, soit dans un onglet navigateur (selon sa configuration interne !).

## 🚀 Pour les Collaborateurs Front-End

- **Répartition des Tâches** : Séparez visuellement vos informations (Une colonne pour le "Live", une colonne pour "L'Historique", etc.).
- **Ne réinventez pas la roue mathématique** : Faites appel aux fonctions définies par vos collègues dans le module `core/analytics.py` plutôt que de refaire les algorithmes de vol ici. Le dossier `ui/` ne doit servir **qu'à l'affichage** !

Bon design !

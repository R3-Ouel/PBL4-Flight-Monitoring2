# 🧠 Module Core : Logique métier et Base de Données

Bienvenue dans le module **Core** !

Considérez ce dossier comme la "salle des machines" ou le "cerveau" logiciel du projet. Il ne traite pas d'affichage ni de capteurs physiques ; son seul but est d'**organiser les données** et de **faire des calculs**.

## 📁 Que contient ce dossier ?

- **`database.py`** : Gère la connexion avec notre base de données en ligne (Supabase). C'est ici que l'on écrit les fonctions pour sauvegarder de nouvelles données de vol (Insert), ou à l'inverse, en récupérer l'historique (Select) pour alimenter le tableau de bord.
- **`analytics.py`** : Le cœur scientifique du projet. C'est ici que la magie de la "Mécanique du Vol" opère. À partir des données brutes (accélération, vitesse, inclinaison), ce module effectue (ou effectuera) les calculs des différentes forces de vol (Traînée, Portance, etc.), le lissage des données, ou la détection d'anomalies de vol.

## 🛠️ Pour les Collaborateurs

### Comment travailler sur le stockage ?
Toute interaction avec la table `telemetrie` de Supabase doit se faire via des fonctions écrites dans `database.py`. Si quelqu'un de l'équipe UI a besoin d'afficher le vol de la semaine dernière, vous devez lui fournir une fonction propre du type `get_flight_data(flight_id)`. Elle s'appuiera sur les clés d'environnement locales (`.env`).

### Comment intégrer des formules scientifiques ?
L'unité d'enseignement traite des forces de l'avion. Si vous devez calculer la portance $P = \frac{1}{2} \cdot \rho \cdot V^2 \cdot S \cdot C_z$, c'est dans `analytics.py` que vous écrirez cette fonction Python, pour qu'elle puisse ensuite être appelée partout ailleurs sans dupliquer de code.

---
**💡 Bonnes pratiques :** 
Veillez à toujours bien documenter (avec des *docstrings*) les fonctions que vous créez ici, car l'équipe du module `ui/` s'en servira énormément !

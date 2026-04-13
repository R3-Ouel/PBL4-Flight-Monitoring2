# frontend — Application Flutter

Cette application Flutter affiche en temps réel les données de télémétrie envoyées par le backend.

## Prérequis

- Flutter SDK installé (voir https://docs.flutter.dev/get-started/install).
- Un appareil cible supporté (Windows, Android, iOS selon la configuration).

## Installation

Depuis le dossier `frontend/` :

```bash
flutter pub get
```

Exécuter l'application (exemples) :

```bash
# Exécution sur l'appareil par défaut
flutter run

# Sur Windows (si le build Windows est configuré)
flutter run -d windows
```

## WebSocket et sources de données

Par défaut, l'application se connecte au WebSocket configuré dans `lib/core/flight_service.dart` :

```dart
const String _wsUrl = 'ws://127.0.0.1:8000/ws/flight-data';
```

Si votre backend tourne sur une autre adresse/port, mettez à jour cette constante.

L'application normalise les champs JSON reçus. Champs attendus :

- `timestamp_ms` (converti en secondes pour l'affichage)
- `altitude`, `vitesse` (ou `speed`), `ax`, `ay`, `az`, `roll`, `pitch`, `yaw`, `phase`, `flight_id`

Exécutez `flutter analyze` si vous souhaitez vérifier les warnings/infos du code. Certaines dépréciations (ex: `withOpacity`) sont informatives et non bloquantes.

## Dépannage

- Pas de connexion : vérifiez que le backend est lancé et que l'URL WebSocket est correcte.
- Données manquantes : vérifiez que le simulateur/posteur envoie bien les champs listés ci-dessus vers `POST /push`.

Pour toute question spécifique sur l'UI, dites-moi quelle vue vous souhaitez documenter (graphes, carte, widgets statistiques), je peux ajouter des explications supplémentaires.

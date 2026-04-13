import 'package:flutter/material.dart';

/// Centralise les couleurs "accent" pour adapter automatiquement
/// l'apparence en mode clair/sombre (réduit le néon en mode light).
class AppColors {
  // In light theme prefer a green-forward accent; keep red neon for dark mode
  static Color accentRed(BuildContext ctx) =>
      Theme.of(ctx).brightness == Brightness.light
      ? Colors.green.shade700
      : Colors.redAccent;
  static Color accentGreen(BuildContext ctx) =>
      Theme.of(ctx).brightness == Brightness.light
      ? Colors.green.shade700
      : Colors.greenAccent;
  static Color accentCyan(BuildContext ctx) =>
      Theme.of(ctx).brightness == Brightness.light
      ? Colors.cyan.shade700
      : Colors.cyanAccent;
  static Color accentPink(BuildContext ctx) =>
      Theme.of(ctx).brightness == Brightness.light
      ? Colors.pink.shade400
      : Colors.pinkAccent;
  static Color accentOrange(BuildContext ctx) =>
      Theme.of(ctx).brightness == Brightness.light
      ? Colors.orange.shade700
      : Colors.orangeAccent;
  static Color accentBlue(BuildContext ctx) =>
      Theme.of(ctx).brightness == Brightness.light
      ? Colors.blue.shade700
      : Colors.blue;
  static Color navInactive(BuildContext ctx) =>
      Theme.of(ctx).brightness == Brightness.light
      ? Colors.black54
      : Colors.white70;
  static Color cardBg(BuildContext ctx) =>
      Theme.of(ctx).brightness == Brightness.light
      ? Colors.grey.shade100
      : const Color(0xFF0D0D1A);
}

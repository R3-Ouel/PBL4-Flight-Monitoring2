import 'package:flutter/material.dart';
import 'package:frontend/ui/dashboard_page.dart';

void main() => runApp(const NeonDashboardApp());

class NeonDashboardApp extends StatefulWidget {
  const NeonDashboardApp({super.key});

  @override
  State<NeonDashboardApp> createState() => _NeonDashboardAppState();
}

class _NeonDashboardAppState extends State<NeonDashboardApp> {
  ThemeMode _themeMode = ThemeMode.dark;

  void _toggleTheme() {
    setState(() {
      _themeMode = _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    });
  }

  @override
  Widget build(BuildContext context) {
    final darkTheme = ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: const Color(0xFF020205),
      colorScheme: const ColorScheme.dark(primary: Colors.redAccent),
      appBarTheme: const AppBarTheme(backgroundColor: Colors.transparent, elevation: 0),
    );

    final lightTheme = ThemeData(
      brightness: Brightness.light,
      // Slightly off-white background to reduce glare in light mode.
      scaffoldBackgroundColor: Colors.grey.shade50,
      colorScheme: ColorScheme.light(primary: Colors.red.shade700),
      appBarTheme: const AppBarTheme(backgroundColor: Colors.transparent, elevation: 0),
      // Make cards and surfaces white and use subtle shadows to reduce eye strain
      cardColor: Colors.white,
      canvasColor: Colors.white,
      cardTheme: CardThemeData(
        color: Colors.white,
        elevation: 0,
        shadowColor: Colors.black12,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      ),
    );

    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: lightTheme,
      darkTheme: darkTheme,
      themeMode: _themeMode,
      home: AnimatedTheme(
        data: _themeMode == ThemeMode.dark ? darkTheme : lightTheme,
        duration: const Duration(milliseconds: 450),
        curve: Curves.easeInOut,
        child: DashboardPage(onToggleTheme: _toggleTheme, isDark: _themeMode == ThemeMode.dark),
      ),
    );
  }
}
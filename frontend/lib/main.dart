import 'package:flutter/material.dart';
import 'package:frontend/ui/dashboard_page.dart';

void main() => runApp(const NeonDashboardApp());

class NeonDashboardApp extends StatelessWidget {
  const NeonDashboardApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF020205),
      ),
      home: const DashboardPage(),
    );
  }
}
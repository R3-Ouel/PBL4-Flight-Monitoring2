import 'package:flutter/material.dart';
import 'package:frontend/core/flight_service.dart';
import 'package:frontend/ui/analyse_view.dart';
import 'package:frontend/ui/navigation_view.dart';
import 'package:frontend/ui/pilotage_view.dart';

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('FLIGHT CONTROL CENTER', style: TextStyle(color: Colors.redAccent, fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 3)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          ValueListenableBuilder<bool>(
            valueListenable: isLive,
            builder: (_, value, __) => Row(
              children: [
                Icon(Icons.wifi, color: value ? Colors.greenAccent : Colors.white24, size: 18),
                const SizedBox(width: 8),
                Text('CONNECTÉ AU DRONE', style: TextStyle(color: value ? Colors.greenAccent : Colors.white24, fontWeight: FontWeight.bold, fontSize: 12)),
                const SizedBox(width: 8),
                Switch(
                  value: value,
                  activeColor: Color.fromARGB(255, 200, 230, 201),
                  activeTrackColor: Colors.greenAccent,
                  inactiveThumbColor: Colors.white38,
                  onChanged: (v) => isLive.value = v,
                ),
                IconButton(
                  icon: const Icon(Icons.restart_alt),
                  color: Colors.white54,
                  tooltip: 'Reset graphs',
                  onPressed: () {
                    resetAllBuffers();
                  },
                ),
              ],
            ),
          ),
          const SizedBox(width: 20),
        ],
      ),
      body: Row(
        children: [
          const NavSidebar(),
          Container(width: 1, color: Colors.white10),
          Expanded(
            child: ValueListenableBuilder<int>(
              valueListenable: navMode,
              builder: (_, mode, __) {
                late Widget child;
                switch (mode) {
                  case 0:
                    child = const AnalyseView(key: ValueKey(0));
                    break;
                  case 1:
                    child = const NavigationView(key: ValueKey(1));
                    break;
                  case 2:
                    child = const PilotageView(key: ValueKey(2));
                    break;
                  default:
                    child = const AnalyseView(key: ValueKey(0));
                }

                return AnimatedSwitcher(
                  duration: const Duration(milliseconds: 350),
                  switchInCurve: Curves.easeInOut,
                  switchOutCurve: Curves.easeInOut,
                  child: child,
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}

class NavSidebar extends StatelessWidget {
  const NavSidebar({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<int>(
      valueListenable: navMode,
      builder: (_, mode, __) => Container(
        width: 64,
        color: const Color(0xFF07070F),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _btn(Icons.bar_chart_rounded, 'Analyse', 0, mode),
            const SizedBox(height: 8),
            _btn(Icons.map_outlined, 'Navigation', 1, mode),
            const SizedBox(height: 8),
            _btn(Icons.gamepad_outlined, 'Pilotage', 2, mode),
          ],
        ),
      ),
    );
  }

  Widget _btn(IconData icon, String label, int index, int current) {
    final bool active = index == current;
    return Tooltip(
      message: label,
      preferBelow: false,
      child: GestureDetector(
        onTap: () => navMode.value = index,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: active ? Colors.redAccent.withOpacity(0.15) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: active ? Colors.redAccent.withOpacity(0.7) : Colors.transparent, width: 1),
          ),
          child: Icon(icon, color: active ? Colors.redAccent : Colors.white38, size: 22),
        ),
      ),
    );
  }
}

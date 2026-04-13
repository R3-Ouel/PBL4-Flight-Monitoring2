import 'package:flutter/material.dart';
import 'package:frontend/core/flight_service.dart';
import 'package:frontend/core/app_colors.dart';
import 'package:frontend/ui/analyse_view.dart';
import 'package:frontend/ui/navigation_view.dart';
import 'package:frontend/ui/pilotage_view.dart';

class DashboardPage extends StatelessWidget {
  final VoidCallback? onToggleTheme;
  final bool isDark;

  const DashboardPage({super.key, this.onToggleTheme, this.isDark = true});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('FLIGHT CONTROL CENTER', style: TextStyle(color: AppColors.accentRed(context), fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 3)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          ValueListenableBuilder<bool>(
            valueListenable: isLive,
            builder: (_, value, __) => Row(
              children: [
                Icon(Icons.wifi, color: value ? AppColors.accentGreen(context) : AppColors.navInactive(context), size: 18),
                const SizedBox(width: 8),
                Text('CONNECTÉ AU DRONE', style: TextStyle(color: value ? AppColors.accentGreen(context) : AppColors.navInactive(context), fontWeight: FontWeight.bold, fontSize: 12)),
                const SizedBox(width: 8),
                Switch(
                  value: value,
                  activeColor: Color.fromARGB(255, 200, 230, 201),
                  activeTrackColor: AppColors.accentGreen(context),
                  inactiveThumbColor: Colors.white38,
                  onChanged: (v) => isLive.value = v,
                ),
                if (onToggleTheme != null)
                  IconButton(
                    icon: AnimatedSwitcher(
                      duration: const Duration(milliseconds: 300),
                      transitionBuilder: (child, anim) => RotationTransition(turns: anim, child: FadeTransition(opacity: anim, child: child)),
                      child: isDark ? const Icon(Icons.nights_stay, key: ValueKey('dark'), color: Colors.white) : const Icon(Icons.wb_sunny, key: ValueKey('light'), color: Colors.yellowAccent),
                    ),
                    tooltip: isDark ? 'Basculer en mode clair' : 'Basculer en mode sombre',
                    onPressed: onToggleTheme,
                  ),
                IconButton(
                  icon: const Icon(Icons.restart_alt),
                  color: AppColors.navInactive(context),
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
        width: 80,
        color: const Color(0xFF07070F),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            _btn(context, Icons.bar_chart_rounded, 'Analyse', 0, mode),
            const SizedBox(height: 8),
            _btn(context, Icons.map_outlined, 'Navigation', 1, mode),
            const SizedBox(height: 8),
            _btn(context, Icons.gamepad_outlined, 'Pilotage', 2, mode),
          ],
        ),
      ),
    );
  }
  Widget _btn(BuildContext ctx, IconData icon, String label, int index, int current) {
    final bool active = index == current;
    final accent = AppColors.accentRed(ctx);
    final inactive = AppColors.navInactive(ctx);
    return Tooltip(
      message: label,
      preferBelow: false,
      child: GestureDetector(
        onTap: () => navMode.value = index,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 200),
          width: 56,
          height: 56,
          decoration: BoxDecoration(
            color: active ? accent.withOpacity(0.15) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: active ? accent.withOpacity(0.7) : Colors.transparent, width: 1),
          ),
          child: Icon(icon, color: active ? accent : inactive, size: 26),
        ),
      ),
    );
  }
}

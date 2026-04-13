import 'package:flutter/material.dart';
import 'package:frontend/widgets/neon_card.dart';
import 'package:frontend/widgets/realtime_value.dart';
import 'package:frontend/widgets/gps_map.dart';
import 'package:frontend/widgets/stat_header.dart';
import 'package:frontend/core/app_colors.dart';

class NavigationView extends StatelessWidget {
  const NavigationView({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const StatHeader(),
          const SizedBox(height: 16),
          Expanded(
            child: Row(
              children: [
                Expanded(flex: 3, child: NeonCard(child: const GpsMapWidget())),
                const SizedBox(width: 16),
                SizedBox(
                  width: 230,
                  child: Builder(builder: (ctx) {
                    final cAlt = AppColors.accentCyan(ctx);
                    final cSpeed = AppColors.accentRed(ctx);
                    final cAz = AppColors.accentPink(ctx);
                    final cRoll = AppColors.accentBlue(ctx);
                    final cPitch = AppColors.accentOrange(ctx);
                    final cYaw = AppColors.accentGreen(ctx);
                    return Column(children: [
                      _param('ALTITUDE', 1, 'm', cAlt),
                      const SizedBox(height: 8),
                      _param('VITESSE', 2, 'm/s', cSpeed),
                      const SizedBox(height: 8),
                      _param('AZ', 5, 'm/s²', cAz),
                      const SizedBox(height: 8),
                      _param('ROLL', 6, '°', cRoll),
                      const SizedBox(height: 8),
                      _param('PITCH', 7, '°', cPitch),
                      const SizedBox(height: 8),
                      _param('YAW', 8, '°', cYaw),
                    ]);
                  }),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _param(String label, int col, String unit, Color color) {
    return NeonCard(
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
          RealTimeValue(columnId: col, unit: unit, color: color),
        ],
      ),
    );
  }
}

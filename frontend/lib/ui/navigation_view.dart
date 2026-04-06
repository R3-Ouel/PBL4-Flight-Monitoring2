import 'package:flutter/material.dart';
import 'package:frontend/widgets/neon_card.dart';
import 'package:frontend/widgets/realtime_value.dart';
import 'package:frontend/widgets/gps_map.dart';
import 'package:frontend/widgets/stat_header.dart';

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
                  child: Column(children: [
                    _param('ALTITUDE', 1, 'm', Colors.cyanAccent),
                    const SizedBox(height: 8),
                    _param('VITESSE', 2, 'm/s', Colors.redAccent),
                    const SizedBox(height: 8),
                    _param('AZ', 5, 'm/s²', Colors.pinkAccent),
                    const SizedBox(height: 8),
                    _param('ROLL', 6, '°', Colors.blue),
                    const SizedBox(height: 8),
                    _param('PITCH', 7, '°', Colors.orange),
                    const SizedBox(height: 8),
                    _param('YAW', 8, '°', Colors.greenAccent),
                  ]),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _param(String label, int col, String unit, Color color) {
    return NeonCard(child: Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [Text(label, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)), RealTimeValue(columnId: col, unit: unit, color: color)]));
  }
}

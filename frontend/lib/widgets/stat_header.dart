import 'package:flutter/material.dart';
import 'package:frontend/widgets/neon_card.dart';
import 'package:frontend/widgets/realtime_value.dart';
import 'package:frontend/core/app_colors.dart';

class StatHeader extends StatelessWidget {
  const StatHeader({super.key});

  @override
  Widget build(BuildContext context) {
    final ctx = context;
    return Row(
      children: [
        _box('ALTITUDE', 1, 'm', AppColors.accentCyan(ctx)),
        const SizedBox(width: 8),
        _box('TEMP. MOTEURS', 10, '°C', AppColors.accentRed(ctx)),
        const SizedBox(width: 8),
        _box('BATTERIE', 11, '%', AppColors.accentPink(ctx)),
        const SizedBox(width: 8),
        _box('TEMPS DE VOL', 0, '', AppColors.accentGreen(ctx), isTimestamp: true),
        const SizedBox(width: 8),
        _box('PHASE DE VOL', 12, '', AppColors.accentOrange(ctx), isPhase: true),
      ],
    );
  }

  Widget _box(String label, int col, String unit, Color color, {bool isTimestamp = false, bool isPhase = false}) {
    return Expanded(
      child: NeonCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(label, style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.bold), maxLines: 1, overflow: TextOverflow.ellipsis),
            const SizedBox(height: 4),
            RealTimeValue(columnId: col, unit: unit, color: color, isTimestamp: isTimestamp, isPhase: isPhase),
          ],
        ),
      ),
    );
  }
}

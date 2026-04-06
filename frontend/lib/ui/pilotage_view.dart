import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:frontend/widgets/neon_card.dart';
import 'package:frontend/widgets/stat_header.dart';

class PilotageView extends StatelessWidget {
  const PilotageView({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(children: [const StatHeader(), const SizedBox(height: 24), Expanded(child: Row(mainAxisAlignment: MainAxisAlignment.spaceEvenly, children: [_joystickCard('THROTTLE / YAW', Colors.redAccent), Column(mainAxisAlignment: MainAxisAlignment.center, children: [_armButton(), const SizedBox(height: 20), const Text('FLIGHT MODE', style: TextStyle(color: Colors.white38, fontSize: 9, letterSpacing: 2)), const SizedBox(height: 10), _modeChip('STABILIZE', Colors.cyanAccent), const SizedBox(height: 6), _modeChip('ALTITUDE HOLD', Colors.greenAccent), const SizedBox(height: 6), _modeChip('AUTO', Colors.orangeAccent)]), _joystickCard('PITCH / ROLL', Colors.cyanAccent)]))]),
    );
  }

  Widget _joystickCard(String label, Color color) => NeonCard(child: SizedBox(width: 220, height: 240, child: Column(children: [Text(label, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1)), const SizedBox(height: 12), Expanded(child: CustomPaint(painter: _JoystickPainter(color: color), size: const Size(180, 180)))])));

  Widget _armButton() => Container(padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14), decoration: BoxDecoration(color: Colors.redAccent.withOpacity(0.12), borderRadius: BorderRadius.circular(10), border: Border.all(color: Colors.redAccent.withOpacity(0.5))), child: const Text('ARM', style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 16, letterSpacing: 4)));

  Widget _modeChip(String label, Color color) => Container(width: 160, padding: const EdgeInsets.symmetric(vertical: 8), decoration: BoxDecoration(color: color.withOpacity(0.05), borderRadius: BorderRadius.circular(6), border: Border.all(color: color.withOpacity(0.2))), child: Text(label, textAlign: TextAlign.center, style: TextStyle(color: color.withOpacity(0.7), fontSize: 10, letterSpacing: 1)));
}

class _JoystickPainter extends CustomPainter {
  final Color color;
  const _JoystickPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final r = math.min(cx, cy) - 6;
    canvas.drawCircle(Offset(cx, cy), r, Paint()..style = PaintingStyle.stroke..color = color.withOpacity(0.25)..strokeWidth = 2);
    canvas.drawCircle(Offset(cx, cy), r * 0.5, Paint()..style = PaintingStyle.stroke..color = color.withOpacity(0.12)..strokeWidth = 1);
    final gp = Paint()..color = color.withOpacity(0.1)..strokeWidth = 1;
    canvas.drawLine(Offset(cx, cy - r), Offset(cx, cy + r), gp);
    canvas.drawLine(Offset(cx - r, cy), Offset(cx + r, cy), gp);
    canvas.drawCircle(Offset(cx, cy), 16, Paint()..color = color.withOpacity(0.12));
    canvas.drawCircle(Offset(cx, cy), 16, Paint()..style = PaintingStyle.stroke..color = color.withOpacity(0.6)..strokeWidth = 1.5);
  }

  @override
  bool shouldRepaint(_JoystickPainter old) => old.color != color;
}

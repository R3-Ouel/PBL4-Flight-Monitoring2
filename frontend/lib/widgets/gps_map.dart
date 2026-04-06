import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:frontend/core/flight_service.dart';

class GpsMapWidget extends StatefulWidget {
  const GpsMapWidget({super.key});
  @override
  State<GpsMapWidget> createState() => _GpsMapWidgetState();
}

class _GpsMapWidgetState extends State<GpsMapWidget> {
  double _yaw = 0;
  double _altitude = 0;
  String _phase = '--';
  StreamSubscription<Map<String, dynamic>>? _sub;

  @override
  void initState() {
    super.initState();
    _sub = flightStream.listen((data) {
      if (mounted) {
        setState(() {
          _yaw = (data['yaw'] as num? ?? 0).toDouble();
          _altitude = (data['altitude'] as num? ?? 0).toDouble();
          _phase = (data['phase'] as String?) ?? _phase;
        });
      }
    });
  }

  @override
  void dispose() { _sub?.cancel(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        ClipRRect(borderRadius: BorderRadius.circular(10), child: CustomPaint(painter: _MapPainter(yaw: _yaw), child: const SizedBox.expand())),
        Positioned(top: 12, left: 12, child: Row(children: [const Icon(Icons.my_location, color: Colors.cyanAccent, size: 13), const SizedBox(width: 6), Text('GPS MAP', style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 11, letterSpacing: 2))])),
        Positioned(top: 10, right: 12, child: _badge('SIMULÉ', Colors.cyanAccent)),
        Positioned(bottom: 12, left: 12, child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [_infoChip('YAW', '${_yaw.toStringAsFixed(1)}°', Colors.greenAccent), const SizedBox(height: 4), _infoChip('ALT', '${_altitude.toStringAsFixed(1)}m', Colors.cyanAccent), const SizedBox(height: 4), _infoChip('PHASE', _phase, Colors.orangeAccent)])),
      ],
    );
  }

  Widget _badge(String text, Color color) => Container(padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3), decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(4), border: Border.all(color: color.withOpacity(0.35))), child: Text(text, style: TextStyle(color: color, fontSize: 9, letterSpacing: 2)));

  Widget _infoChip(String label, String value, Color color) => Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4), decoration: BoxDecoration(color: const Color(0xBB050512), borderRadius: BorderRadius.circular(6), border: Border.all(color: color.withOpacity(0.3))), child: Row(children: [Text('$label  ', style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.bold)), Text(value, style: TextStyle(color: Colors.white.withOpacity(0.85), fontSize: 11, fontWeight: FontWeight.bold))]));
}

class _MapPainter extends CustomPainter {
  final double yaw;
  const _MapPainter({required this.yaw});

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height), Paint()..color = const Color(0xFF050512));
    final g = Paint()..color = Colors.white.withOpacity(0.04)..strokeWidth = 1;
    for (double x = 0; x < size.width; x += 40) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), g);
    }
    for (double y = 0; y < size.height; y += 40) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), g);
    }
    final circlePaint = Paint()..style = PaintingStyle.stroke..color = Colors.cyanAccent.withOpacity(0.07)..strokeWidth = 1;
    for (double r = 50; r < math.max(size.width, size.height); r += 60) {
      canvas.drawCircle(Offset(cx, cy), r, circlePaint);
    }
    final cross = Paint()..color = Colors.white.withOpacity(0.08)..strokeWidth = 1;
    canvas.drawLine(Offset(cx, 0), Offset(cx, size.height), cross);
    canvas.drawLine(Offset(0, cy), Offset(size.width, cy), cross);
    canvas.drawCircle(Offset(cx, cy), 22, Paint()..style = PaintingStyle.stroke..color = Colors.cyanAccent.withOpacity(0.25)..strokeWidth = 1.5);
    canvas.save();
    canvas.translate(cx, cy);
    canvas.rotate(yaw * math.pi / 180);
    const d = 14.0;
    final path = Path()..moveTo(0, -d)..lineTo(d * 0.6, d * 0.7)..lineTo(-d * 0.6, d * 0.7)..close();
    canvas.drawPath(path, Paint()..color = Colors.cyanAccent);
    canvas.restore();
  }

  @override
  bool shouldRepaint(_MapPainter old) => old.yaw != yaw;
}

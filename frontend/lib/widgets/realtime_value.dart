import 'package:flutter/material.dart';
import 'package:frontend/core/flight_service.dart';

class RealTimeValue extends StatefulWidget {
  final int columnId;
  final String unit;
  final Color color;
  final bool isTimestamp;
  final bool isPhase;

  const RealTimeValue({super.key, required this.columnId, required this.unit, required this.color, this.isTimestamp = false, this.isPhase = false});

  @override
  State<RealTimeValue> createState() => _RealTimeValueState();
}

class _RealTimeValueState extends State<RealTimeValue> {
  double _lastValue = 0.0;
  String _lastPhase = '--';

  String _formatTs(double s) {
    final t = s.toInt();
    final h = t ~/ 3600;
    final m = (t % 3600) ~/ 60;
    final sec = t % 60;
    return '${h.toString().padLeft(2,'0')}:${m.toString().padLeft(2,'0')}:${sec.toString().padLeft(2,'0')}';
  }

  double? _extract(Map<String, dynamic> data) {
    switch (widget.columnId) {
      case 0:
        return (data['timestamp'] as num?)?.toDouble();
      case 1:
        return (data['altitude'] as num?)?.toDouble();
      case 2:
        return (data['speed'] as num?)?.toDouble();
      case 5:
        return (data['az'] as num?)?.toDouble();
      case 6:
        return (data['roll'] as num?)?.toDouble();
      case 7:
        return (data['pitch'] as num?)?.toDouble();
      case 8:
        return (data['yaw'] as num?)?.toDouble();
      default:
        return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Map<String, dynamic>>(
      stream: flightStream,
      builder: (_, snap) {
        if (snap.hasData) {
          if (widget.isPhase) {
            _lastPhase = (snap.data!['phase'] as String?) ?? _lastPhase;
          } else {
            final v = _extract(snap.data!);
            if (v != null) _lastValue = v;
          }
        }

        final connected = snap.connectionState == ConnectionState.active && !snap.hasError;

        if (widget.isPhase) {
          return Row(children: [ _dot(connected), const SizedBox(width: 4), Flexible(child: Text(_lastPhase, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: widget.color), overflow: TextOverflow.ellipsis))]);
        }

        if (widget.isTimestamp) {
          return Row(children: [ _dot(connected), const SizedBox(width: 4), Text(_formatTs(_lastValue), style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: widget.color))]);
        }

        return Text('${_lastValue.toStringAsFixed(1)}${widget.unit}', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: widget.color));
      },
    );
  }

  Widget _dot(bool connected) => Container(width: 6, height: 6, decoration: BoxDecoration(shape: BoxShape.circle, color: connected ? Colors.greenAccent : Colors.redAccent, boxShadow: [BoxShadow(color: (connected ? Colors.greenAccent : Colors.redAccent).withOpacity(0.6), blurRadius: 4)]));
}

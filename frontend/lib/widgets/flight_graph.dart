import 'dart:async';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:frontend/core/flight_service.dart';

class RealTimeGraph extends StatefulWidget {
  final List<int> columnIds;
  final List<Color> colors;
  const RealTimeGraph({super.key, required this.columnIds, required this.colors});

  @override
  State<RealTimeGraph> createState() => _RealTimeGraphState();
}

class _RealTimeGraphState extends State<RealTimeGraph> {
  StreamSubscription<void>? _bufSub;

  @override
  void initState() {
    super.initState();
    // Rebuild whenever FlightService buffers update so graphs stay in sync across pages
    _bufSub = bufferStream.listen((_) {
      if (!mounted) return;
      setState(() {});
    });
  }

  String _keyForId(int id) {
    switch (id) {
      case 0:
        return 'timestamp';
      case 1:
        return 'altitude';
      case 2:
        return 'speed';
      case 5:
        return 'az';
      case 6:
        return 'roll';
      case 7:
        return 'pitch';
      case 8:
        return 'yaw';
      default:
        return '';
    }
  }

  @override
  void dispose() {
    _bufSub?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Build spots from the shared buffers maintained in FlightService
    final allSpots = List.generate(widget.columnIds.length, (i) {
      final key = _keyForId(widget.columnIds[i]);
      if (key.isEmpty) return <FlSpot>[];
      final buf = getBufferForKey(key);
      final spots = buf.map((p) => FlSpot(p[0], p[1])).toList();
      // ensure spots are ordered by X (timestamp)
      spots.sort((a, b) => a.x.compareTo(b.x));
      // ensure strictly increasing X values to avoid fl_chart curve artifacts
      for (int j = 1; j < spots.length; j++) {
        if (spots[j].x <= spots[j - 1].x) {
          final newX = spots[j - 1].x + 0.001; // small epsilon (ms-level)
          spots[j] = FlSpot(newX, spots[j].y);
        }
      }
      return spots;
    });

    final bool hasData = allSpots.any((s) => s.isNotEmpty);
    if (!hasData) return const Center(child: CircularProgressIndicator());

    double minX = double.infinity, maxX = double.negativeInfinity;
    double minY = double.infinity, maxY = double.negativeInfinity;
    for (final list in allSpots) {
      for (final p in list) {
        minX = math.min(minX, p.x);
        maxX = math.max(maxX, p.x);
        minY = math.min(minY, p.y);
        maxY = math.max(maxY, p.y);
      }
    }
    if (minX == double.infinity || maxX == double.negativeInfinity) {
      minX = 0;
      maxX = 1;
    }
    // ensure a non-zero X range for fl_chart
    if ((maxX - minX).abs() < 1e-9) {
      minX -= 1.0;
      maxX += 1.0;
    }
    if (minY == double.infinity || maxY == double.negativeInfinity) {
      minY = 0;
      maxY = 1;
    }

    final ySpan = (maxY - minY).abs();
    final pad = ySpan == 0 ? 1.0 : ySpan * 0.12;
    minY -= pad;
    maxY += pad;

    // format helper: display elapsed time relative to minX as mm:ss or hh:mm:ss
    String _fmt(double seconds) {
      final elapsed = Duration(seconds: (seconds - minX).round());
      final h = elapsed.inHours;
      final m = elapsed.inMinutes.remainder(60);
      final s = elapsed.inSeconds.remainder(60);
      if (h > 0) return '${h.toString().padLeft(2, '0')}:${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
      return '${m.toString().padLeft(2, '0')}:${s.toString().padLeft(2, '0')}';
    }

    // prepare bottom ticks (min, 1/4, 1/2, 3/4, max) to show readable labels
    final span = maxX - minX;
    final ticks = <double>[minX, minX + span * 0.25, minX + span * 0.5, minX + span * 0.75, maxX];

    return LineChart(
      LineChartData(
        minX: minX,
        maxX: maxX,
        minY: minY,
        maxY: maxY,
        gridData: FlGridData(
          show: true,
          drawVerticalLine: false,
          getDrawingHorizontalLine: (value) => FlLine(color: Colors.white.withOpacity(0.03), strokeWidth: 1),
        ),
        titlesData: FlTitlesData(
          topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
          bottomTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 28, getTitlesWidget: (value, meta) {
            // display labels only for prepared ticks (within tolerance)
            const tol = 0.02; // relative tolerance
            for (final t in ticks) {
              if ((value - t).abs() <= (span * tol)) {
                return Text(_fmt(value), style: const TextStyle(color: Colors.white54, fontSize: 10));
              }
            }
            return const SizedBox.shrink();
          })),
          leftTitles: AxisTitles(sideTitles: SideTitles(showTitles: true, reservedSize: 40, getTitlesWidget: (value, meta) {
            return Text(value.toStringAsFixed(0), style: const TextStyle(color: Colors.white24, fontSize: 10));
          })),
        ),
        borderData: FlBorderData(show: false),
        lineBarsData: List.generate(widget.columnIds.length, (i) {
          return LineChartBarData(
            spots: allSpots[i],
            isCurved: false,
            color: widget.colors[i],
            barWidth: 2,
            dotData: const FlDotData(show: false),
            belowBarData: BarAreaData(show: true, color: widget.colors[i].withOpacity(0.06)),
          );
        }),
      ),
    );
  }
}

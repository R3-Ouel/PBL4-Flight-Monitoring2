import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() {
  runApp(const NeonDashboardApp());
}

// Contrôleur global pour le bouton ON/OFF
ValueNotifier<bool> isLive = ValueNotifier<bool>(true);

// URL du backend WebSocket
const String _wsUrl = 'ws://127.0.0.1:8000/ws/flight-data';

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

// ─── FlightService avec reconnexion automatique ───────────────────────────────
class FlightService {
  final _controller = StreamController<Map<String, dynamic>>.broadcast();
  WebSocketChannel? _channel;
  bool _disposed = false;

  FlightService() {
    _connect();
  }

  void _connect() async {
    if (_disposed) return;
    try {
      _channel = WebSocketChannel.connect(Uri.parse(_wsUrl));
      _channel!.stream.listen(
            (event) {
          try {
            final raw = jsonDecode(event) as Map<String, dynamic>;
            _controller.add({
              'timestamp': (raw['timestamp_ms'] ?? 0) / 1000.0,
              'altitude':  (raw['altitude'] ?? 0).toDouble(),
              'speed':     (raw['vitesse'] ?? raw['speed'] ?? 0).toDouble(),
              'ax':        (raw['ax'] ?? 0).toDouble(),
              'ay':        (raw['ay'] ?? 0).toDouble(),
              'az':        (raw['az'] ?? 0).toDouble(),
              'roll':      (raw['roll'] ?? 0).toDouble(),
              'pitch':     (raw['pitch'] ?? 0).toDouble(),
              'yaw':       (raw['yaw'] ?? 0).toDouble(),
              'phase':     raw['phase'] ?? '',
              'battery':   (raw['battery'] ?? raw['batterie'] ?? 0).toDouble(),
              'latitude':  (raw['latitude'] ?? 0).toDouble(),
              'longitude': (raw['longitude'] ?? 0).toDouble(),
            });
          } catch (_) {}
        },
        onDone: () {
          // Reconnexion automatique après déconnexion
          if (!_disposed) {
            Future.delayed(const Duration(seconds: 2), _connect);
          }
        },
        onError: (_) {
          if (!_disposed) {
            Future.delayed(const Duration(seconds: 2), _connect);
          }
        },
        cancelOnError: false,
      );
    } catch (_) {
      if (!_disposed) {
        Future.delayed(const Duration(seconds: 2), _connect);
      }
    }
  }

  Stream<Map<String, dynamic>> get stream => _controller.stream;

  void dispose() {
    _disposed = true;
    _channel?.sink.close();
    _controller.close();
  }
}

// Stream global partagé par toute l'app
final _flightService = FlightService();
Stream<Map<String, dynamic>> get flightStream => _flightService.stream;

class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("FLIGHT CONTROLER CENTER",
            style: TextStyle(color: Colors.redAccent, fontSize: 18, fontWeight: FontWeight.bold, letterSpacing: 3)),
        backgroundColor: Colors.transparent,
        actions: [
          ValueListenableBuilder<bool>(
            valueListenable: isLive,
            builder: (context, value, child) {
              return Row(
                children: [
                  Text(value ? "LIVE" : "PAUSED",
                      style: TextStyle(color: value ? Colors.greenAccent : Colors.white24, fontWeight: FontWeight.bold, fontSize: 12)),
                  Switch(
                    value: value,
                    thumbColor: WidgetStateProperty.resolveWith(
                          (states) => states.contains(WidgetState.selected)
                          ? Colors.greenAccent
                          : Colors.white38,
                    ),
                    onChanged: (newValue) => isLive.value = newValue,
                  ),
                ],
              );
            },
          ),
          const SizedBox(width: 20),
        ],
        elevation: 0,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // --- LES 5 BOXES SUR LA MÊME LIGNE ---
            Row(
              children: [
                _buildStatBox("ALTITUDE", 1, "m", Colors.cyanAccent),
                const SizedBox(width: 8),
                _buildStatBox("TEMP. MOTEURS", 10, "°C", Colors.redAccent),
                const SizedBox(width: 8),
                _buildStatBox("BATTERIE", 11, "%", Colors.pinkAccent),
                const SizedBox(width: 8),
                _buildStatBox("TEMPS DE VOL", 0, "", Colors.greenAccent, isTimestamp: true),
                const SizedBox(width: 8),
                _buildStatBox("PHASE DE VOL", 12, "", Colors.orangeAccent, isPhase: true),
              ],
            ),
            const SizedBox(height: 30),
            // --- GRAPHIQUES ---
            Wrap(
              spacing: 20,
              runSpacing: 20,
              alignment: WrapAlignment.center,
              children: [
                _buildGraphBox("PROFIL DE MONTÉE (Altitude)", [1], [Colors.cyanAccent]),
                _buildGraphBox("VITESSE DE VOL", [2], [Colors.redAccent]),
                _buildGraphBox("ACCÉLÉRATION VERTICALE (AZ)", [5], [Colors.pinkAccent]),
                _buildGraphBox("ORIENTATION (Roll, Pitch, Yaw)", [6, 7, 8], [Colors.blue, Colors.orange, Colors.greenAccent]),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatBox(String label, int col, String unit, Color color, {bool isTimestamp = false, bool isPhase = false}) {
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

  Widget _buildGraphBox(String title, List<int> cols, List<Color> colors) {
    return SizedBox(
      width: 720,
      height: 350,
      child: NeonCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            const SizedBox(height: 5),
            if (cols.length > 1)
              Row(
                children: [
                  _legendItem("Roll", Colors.blue),
                  _legendItem("Pitch", Colors.orange),
                  _legendItem("Yaw", Colors.greenAccent),
                ],
              ),
            const SizedBox(height: 10),
            Expanded(child: RealTimeGraph(columnIds: cols, colors: colors)),
          ],
        ),
      ),
    );
  }

  Widget _legendItem(String name, Color col) {
    return Padding(
      padding: const EdgeInsets.only(right: 15),
      child: Row(children: [
        Container(width: 10, height: 10, color: col),
        const SizedBox(width: 5),
        Text(name, style: const TextStyle(fontSize: 10))
      ]),
    );
  }
}

// ─── RealTimeValue — garde la dernière valeur reçue en mémoire ───────────────
class RealTimeValue extends StatefulWidget {
  final int columnId;
  final String unit;
  final Color color;
  final bool isTimestamp;
  final bool isPhase;

  const RealTimeValue({
    super.key,
    required this.columnId,
    required this.unit,
    required this.color,
    this.isTimestamp = false,
    this.isPhase = false,
  });

  @override
  State<RealTimeValue> createState() => _RealTimeValueState();
}

class _RealTimeValueState extends State<RealTimeValue> {
  // Valeur par défaut : 0 (ou "00:00:00" pour timestamp, "--" pour phase)
  double _lastValue = 0.0;
  String _lastPhase = '--';

  String _formatTimestamp(double seconds) {
    int s = seconds.toInt();
    int h = s ~/ 3600;
    int m = (s % 3600) ~/ 60;
    int sec = s % 60;
    return "${h.toString().padLeft(2, '0')}:${m.toString().padLeft(2, '0')}:${sec.toString().padLeft(2, '0')}";
  }

  /// Extrait la valeur numérique correspondant au columnId depuis le payload.
  double? _extractValue(Map<String, dynamic> data) {
    switch (widget.columnId) {
      case 0:  return (data['timestamp'] as num?)?.toDouble();
      case 1:  return (data['altitude']  as num?)?.toDouble();
      case 2:  return (data['speed']     as num?)?.toDouble();
      case 5:  return (data['az']        as num?)?.toDouble();
      case 6:  return (data['roll']      as num?)?.toDouble();
      case 7:  return (data['pitch']     as num?)?.toDouble();
      case 8:  return (data['yaw']       as num?)?.toDouble();
      case 11: return (data['battery']   as num?)?.toDouble();
      default: return null;
    }
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Map<String, dynamic>>(
      stream: flightStream,
      builder: (context, snapshot) {
        // Mettre à jour la dernière valeur connue dès qu'on reçoit des données
        if (snapshot.hasData) {
          final data = snapshot.data!;

          if (widget.isPhase) {
            _lastPhase = (data['phase'] as String?) ?? _lastPhase;
          } else {
            final v = _extractValue(data);
            if (v != null) _lastValue = v;
          }
        }

        // Indicateur de connexion : petit point coloré
        final bool connected = snapshot.connectionState == ConnectionState.active
            && !snapshot.hasError;

        // Rendu phase
        if (widget.isPhase) {
          return Row(
            children: [
              _connectionDot(connected),
              const SizedBox(width: 4),
              Text(
                _lastPhase,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: widget.color,
                ),
              ),
            ],
          );
        }

        // Rendu timestamp
        if (widget.isTimestamp) {
          return Row(
            children: [
              _connectionDot(connected),
              const SizedBox(width: 4),
              Text(
                _formatTimestamp(_lastValue),
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: widget.color,
                ),
              ),
            ],
          );
        }

        // Rendu valeur numérique standard
        return Text(
          '${_lastValue.toStringAsFixed(1)}${widget.unit}',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: widget.color,
          ),
        );
      },
    );
  }

  /// Point vert = connecté, rouge = coupure / attente
  Widget _connectionDot(bool connected) {
    return Container(
      width: 6,
      height: 6,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: connected ? Colors.greenAccent : Colors.redAccent,
        boxShadow: [BoxShadow(color: (connected ? Colors.greenAccent : Colors.redAccent).withValues(alpha: 0.6), blurRadius: 4)],
      ),
    );
  }
}

// ─── RealTimeGraph — accumule les points dans le state ───────────────────────
class RealTimeGraph extends StatefulWidget {
  final List<int> columnIds;
  final List<Color> colors;
  const RealTimeGraph({super.key, required this.columnIds, required this.colors});

  @override
  State<RealTimeGraph> createState() => _RealTimeGraphState();
}

class _RealTimeGraphState extends State<RealTimeGraph> {
  late List<List<FlSpot>> _allSpots;
  StreamSubscription<Map<String, dynamic>>? _sub;

  @override
  void initState() {
    super.initState();
    _allSpots = List.generate(widget.columnIds.length, (_) => []);
    _sub = flightStream.listen((data) {
      if (!isLive.value) return; // on n'accumule pas quand PAUSED

      final double x = (data['timestamp'] as num? ?? 0).toDouble();

      setState(() {
        for (int i = 0; i < widget.columnIds.length; i++) {
          final String key = switch (widget.columnIds[i]) {
            1 => 'altitude',
            2 => 'speed',
            5 => 'az',
            6 => 'roll',
            7 => 'pitch',
            8 => 'yaw',
            _ => '',
          };
          if (key.isNotEmpty && data[key] != null) {
            final double y = (data[key] as num).toDouble();
            _allSpots[i].add(FlSpot(x, y));
          }
        }
      });
    });
  }

  @override
  void dispose() {
    _sub?.cancel();
    super.dispose();
  }

  List<LineChartBarData> _buildBars() {
    return List.generate(widget.columnIds.length, (i) => LineChartBarData(
      spots: _allSpots[i],
      isCurved: true,
      color: widget.colors[i],
      barWidth: 3,
      dotData: const FlDotData(show: false),
      shadow: Shadow(blurRadius: 10, color: widget.colors[i].withValues(alpha: 0.5)),
      belowBarData: BarAreaData(show: i == 0, color: widget.colors[i].withValues(alpha: 0.05)),
    ));
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: isLive,
      builder: (context, live, child) {
        if (!live) {
          return const Center(
            child: Text('SYSTEM PAUSED', style: TextStyle(color: Colors.white12, letterSpacing: 5)),
          );
        }

        final bars = _buildBars();
        // Pas encore de données : spinner
        if (bars.isEmpty || bars.every((b) => b.spots.isEmpty)) {
          return const Center(child: CircularProgressIndicator());
        }

        return LineChart(
          LineChartData(
            gridData: FlGridData(
              show: true,
              getDrawingHorizontalLine: (_) => FlLine(color: Colors.white.withValues(alpha: 0.05)),
            ),
            titlesData: FlTitlesData(
              show: true,
              topTitles: const AxisTitles(),
              rightTitles: const AxisTitles(),
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(showTitles: true, reservedSize: 30, interval: 20),
              ),
              leftTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 45,
                  getTitlesWidget: (value, meta) {
                    if (value == meta.max || value == meta.min) return const SizedBox();
                    return Text(
                      value.toStringAsFixed(1),
                      style: const TextStyle(color: Colors.white24, fontSize: 10),
                    );
                  },
                ),
              ),
            ),
            borderData: FlBorderData(show: false),
            lineBarsData: bars,
          ),
        );
      },
    );
  }
}


class NeonCard extends StatelessWidget {
  final Widget child;
  const NeonCard({super.key, required this.child});
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFF0D0D1A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: child,
    );
  }
}
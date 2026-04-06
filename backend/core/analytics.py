import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

void main() => runApp(const NeonDashboardApp());

// ── Globals ───────────────────────────────────────────────────────────────────
final ValueNotifier<bool> isLive  = ValueNotifier<bool>(false);
final ValueNotifier<int>  navMode = ValueNotifier<int>(0);
// 0 = Analyse | 1 = Navigation | 2 = Pilotage

const String _wsUrl          = 'ws://127.0.0.1:8000/ws/flight-data';
const int    _maxGraphPoints  = 150; // fenêtre glissante

// ── FlightService — reconnexion automatique ───────────────────────────────────
class FlightService {
  final _controller = StreamController<Map<String, dynamic>>.broadcast();
  WebSocketChannel? _channel;
  bool _disposed = false;

  FlightService() { _connect(); }

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
              'altitude':  (raw['altitude']  ?? 0).toDouble(),
              'speed':     (raw['vitesse']   ?? raw['speed'] ?? 0).toDouble(),
              'ax':        (raw['ax']        ?? 0).toDouble(),
              'ay':        (raw['ay']        ?? 0).toDouble(),
              'az':        (raw['az']        ?? 0).toDouble(),
              'roll':      (raw['roll']      ?? 0).toDouble(),
              'pitch':     (raw['pitch']     ?? 0).toDouble(),
              'yaw':       (raw['yaw']       ?? 0).toDouble(),
              'phase':     raw['phase']      ?? '',
            });
          } catch (_) {}
        },
        onDone:  () { if (!_disposed) Future.delayed(const Duration(seconds: 2), _connect); },
        onError: (_) { if (!_disposed) Future.delayed(const Duration(seconds: 2), _connect); },
        cancelOnError: false,
      );
    } catch (_) {
      if (!_disposed) Future.delayed(const Duration(seconds: 2), _connect);
    }
  }

  Stream<Map<String, dynamic>> get stream => _controller.stream;

  void dispose() {
    _disposed = true;
    _channel?.sink.close();
    _controller.close();
  }
}

final _flightService = FlightService();
Stream<Map<String, dynamic>> get flightStream => _flightService.stream;

// ── App ───────────────────────────────────────────────────────────────────────
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

// ── DashboardPage ─────────────────────────────────────────────────────────────
class DashboardPage extends StatelessWidget {
  const DashboardPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'FLIGHT CONTROL CENTER',
          style: TextStyle(
            color: Colors.redAccent, fontSize: 18,
            fontWeight: FontWeight.bold, letterSpacing: 3,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          ValueListenableBuilder<bool>(
            valueListenable: isLive,
            builder: (_, value, __) => Row(
              children: [
                Text(
                  value ? 'LIVE' : 'PAUSED',
                  style: TextStyle(
                    color: value ? Colors.greenAccent : Colors.white24,
                    fontWeight: FontWeight.bold, fontSize: 12,
                  ),
                ),
                Switch(
                  value: value,
                  thumbColor: WidgetStateProperty.resolveWith(
                    (s) => s.contains(WidgetState.selected)
                        ? Colors.greenAccent
                        : Colors.white38,
                  ),
                  onChanged: (v) => isLive.value = v,
                ),
              ],
            ),
          ),
          const SizedBox(width: 20),
        ],
      ),
      body: Row(
        children: [
          // ── Sidebar ──
          const NavSidebar(),
          Container(width: 1, color: Colors.white10),
          // ── Contenu selon le mode ──
          Expanded(
            child: ValueListenableBuilder<int>(
              valueListenable: navMode,
              builder: (_, mode, __) => switch (mode) {
                0 => const AnalyseView(),
                1 => const NavigationView(),
                2 => const PilotageView(),
                _ => const AnalyseView(),
              },
            ),
          ),
        ],
      ),
    );
  }
}

// ── NavSidebar ────────────────────────────────────────────────────────────────
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
            _btn(Icons.bar_chart_rounded, 'Analyse',    0, mode),
            const SizedBox(height: 8),
            _btn(Icons.map_outlined,      'Navigation', 1, mode),
            const SizedBox(height: 8),
            _btn(Icons.gamepad_outlined,  'Pilotage',   2, mode),
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
            color: active
                ? Colors.redAccent.withValues(alpha: 0.15)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: active
                  ? Colors.redAccent.withValues(alpha: 0.7)
                  : Colors.transparent,
              width: 1,
            ),
          ),
          child: Icon(
            icon,
            color: active ? Colors.redAccent : Colors.white38,
            size: 22,
          ),
        ),
      ),
    );
  }
}

// ── StatHeader — bande commune à tous les modes ───────────────────────────────
class StatHeader extends StatelessWidget {
  const StatHeader({super.key});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        _box('ALTITUDE',      1,  'm',   Colors.cyanAccent),
        const SizedBox(width: 8),
        _box('TEMP. MOTEURS', 10, '°C',  Colors.redAccent),
        const SizedBox(width: 8),
        _box('PRESSION ATM.', 11, 'hPa', Colors.pinkAccent),
        const SizedBox(width: 8),
        _box('TEMPS DE VOL',  0,  '',    Colors.greenAccent, isTimestamp: true),
        const SizedBox(width: 8),
        _box('PHASE DE VOL',  12, '',    Colors.orangeAccent, isPhase: true),
      ],
    );
  }

  Widget _box(String label, int col, String unit, Color color,
      {bool isTimestamp = false, bool isPhase = false}) {
    return Expanded(
      child: NeonCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(
              label,
              style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.bold),
              maxLines: 1, overflow: TextOverflow.ellipsis,
            ),
            const SizedBox(height: 4),
            RealTimeValue(
              columnId: col, unit: unit, color: color,
              isTimestamp: isTimestamp, isPhase: isPhase,
            ),
          ],
        ),
      ),
    );
  }
}

// ────────────────────────────────────────────────────────────────────────────
// ── MODE 0 : ANALYSE ────────────────────────────────────────────────────────
// ────────────────────────────────────────────────────────────────────────────
class AnalyseView extends StatelessWidget {
  const AnalyseView({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const StatHeader(),
          const SizedBox(height: 24),
          Wrap(
            spacing: 16,
            runSpacing: 16,
            alignment: WrapAlignment.center,
            children: [
              _graph('PROFIL DE MONTÉE (Altitude)',     [1],       [Colors.cyanAccent]),
              _graph('VITESSE DE VOL',                  [2],       [Colors.redAccent]),
              _graph('ACCÉLÉRATION VERTICALE (AZ)',     [5],       [Colors.pinkAccent]),
              _graph('ORIENTATION (Roll, Pitch, Yaw)',  [6, 7, 8], [Colors.blue, Colors.orange, Colors.greenAccent]),
            ],
          ),
        ],
      ),
    );
  }

  Widget _graph(String title, List<int> cols, List<Color> colors) {
    return SizedBox(
      width: 680,
      height: 280,
      child: NeonCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(
                      color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12,
                    ),
                  ),
                ),
                if (cols.length > 1) ...[
                  _legend('Roll',  Colors.blue),
                  _legend('Pitch', Colors.orange),
                  _legend('Yaw',   Colors.greenAccent),
                ],
              ],
            ),
            const SizedBox(height: 10),
            Expanded(
              // RepaintBoundary isole les repaints du graphique
              child: RepaintBoundary(
                child: RealTimeGraph(columnIds: cols, colors: colors),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _legend(String name, Color col) => Padding(
    padding: const EdgeInsets.only(left: 12),
    child: Row(children: [
      Container(width: 8, height: 8, color: col),
      const SizedBox(width: 4),
      Text(name, style: const TextStyle(fontSize: 9, color: Colors.white54)),
    ]),
  );
}

// ────────────────────────────────────────────────────────────────────────────
// ── MODE 1 : NAVIGATION ──────────────────────────────────────────────────────
// ────────────────────────────────────────────────────────────────────────────
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
                // ── Carte GPS ──
                Expanded(
                  flex: 3,
                  child: NeonCard(child: const GpsMapWidget()),
                ),
                const SizedBox(width: 16),
                // ── Panneau paramètres ──
                SizedBox(
                  width: 230,
                  child: Column(
                    children: [
                      _param('ALTITUDE', 1, 'm',    Colors.cyanAccent),
                      const SizedBox(height: 8),
                      _param('VITESSE',  2, 'm/s',  Colors.redAccent),
                      const SizedBox(height: 8),
                      _param('AZ',       5, 'm/s²', Colors.pinkAccent),
                      const SizedBox(height: 8),
                      _param('ROLL',     6, '°',    Colors.blue),
                      const SizedBox(height: 8),
                      _param('PITCH',    7, '°',    Colors.orange),
                      const SizedBox(height: 8),
                      _param('YAW',      8, '°',    Colors.greenAccent),
                    ],
                  ),
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
          Text(label,
              style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
          RealTimeValue(columnId: col, unit: unit, color: color),
        ],
      ),
    );
  }
}

// ── GpsMapWidget ──────────────────────────────────────────────────────────────
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
      if (mounted) setState(() {
        _yaw      = (data['yaw']      as num? ?? 0).toDouble();
        _altitude = (data['altitude'] as num? ?? 0).toDouble();
        _phase    = (data['phase']    as String?) ?? _phase;
      });
    });
  }

  @override
  void dispose() { _sub?.cancel(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Fond + dessin carte
        ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: CustomPaint(
            painter: _MapPainter(yaw: _yaw),
            child: const SizedBox.expand(),
          ),
        ),
        // Overlay infos
        Positioned(
          top: 12, left: 12,
          child: Row(children: [
            const Icon(Icons.my_location, color: Colors.cyanAccent, size: 13),
            const SizedBox(width: 6),
            Text('GPS MAP', style: TextStyle(
                color: Colors.white.withValues(alpha: 0.7), fontSize: 11, letterSpacing: 2)),
          ]),
        ),
        Positioned(
          top: 10, right: 12,
          child: _badge('SIMULÉ', Colors.cyanAccent),
        ),
        Positioned(
          bottom: 12, left: 12,
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            _infoChip('YAW',   '${_yaw.toStringAsFixed(1)}°',    Colors.greenAccent),
            const SizedBox(height: 4),
            _infoChip('ALT',   '${_altitude.toStringAsFixed(1)}m', Colors.cyanAccent),
            const SizedBox(height: 4),
            _infoChip('PHASE', _phase,                             Colors.orangeAccent),
          ]),
        ),
      ],
    );
  }

  Widget _badge(String text, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(
      color: color.withValues(alpha: 0.1),
      borderRadius: BorderRadius.circular(4),
      border: Border.all(color: color.withValues(alpha: 0.35)),
    ),
    child: Text(text, style: TextStyle(color: color, fontSize: 9, letterSpacing: 2)),
  );

  Widget _infoChip(String label, String value, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
    decoration: BoxDecoration(
      color: const Color(0xBB050512),
      borderRadius: BorderRadius.circular(6),
      border: Border.all(color: color.withValues(alpha: 0.3)),
    ),
    child: Row(children: [
      Text('$label  ', style: TextStyle(color: color, fontSize: 9, fontWeight: FontWeight.bold)),
      Text(value, style: TextStyle(color: Colors.white.withValues(alpha: 0.85), fontSize: 11, fontWeight: FontWeight.bold)),
    ]),
  );
}

class _MapPainter extends CustomPainter {
  final double yaw;
  const _MapPainter({required this.yaw});

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;

    // Fond
    canvas.drawRect(Rect.fromLTWH(0, 0, size.width, size.height),
        Paint()..color = const Color(0xFF050512));

    // Grille
    final g = Paint()..color = Colors.white.withValues(alpha: 0.04)..strokeWidth = 1;
    for (double x = 0; x < size.width; x += 40) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), g);
    }
    for (double y = 0; y < size.height; y += 40) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), g);
    }

    // Cercles concentriques
    final circlePaint = Paint()
      ..style = PaintingStyle.stroke
      ..color = Colors.cyanAccent.withValues(alpha: 0.07)
      ..strokeWidth = 1;
    for (double r = 50; r < math.max(size.width, size.height); r += 60) {
      canvas.drawCircle(Offset(cx, cy), r, circlePaint);
    }

    // Axes crosshair
    final cross = Paint()..color = Colors.white.withValues(alpha: 0.08)..strokeWidth = 1;
    canvas.drawLine(Offset(cx, 0), Offset(cx, size.height), cross);
    canvas.drawLine(Offset(0, cy), Offset(size.width, cy),  cross);

    // Anneau de glow autour du drone
    canvas.drawCircle(Offset(cx, cy), 22,
        Paint()
          ..style = PaintingStyle.stroke
          ..color = Colors.cyanAccent.withValues(alpha: 0.25)
          ..strokeWidth = 1.5);

    // Drone — triangle orienté selon yaw
    canvas.save();
    canvas.translate(cx, cy);
    canvas.rotate(yaw * math.pi / 180);
    const d = 14.0;
    final path = Path()
      ..moveTo(0, -d)
      ..lineTo(d * 0.6, d * 0.7)
      ..lineTo(-d * 0.6, d * 0.7)
      ..close();
    canvas.drawPath(path, Paint()..color = Colors.cyanAccent);
    canvas.restore();
  }

  @override
  bool shouldRepaint(_MapPainter old) => old.yaw != yaw;
}

// ────────────────────────────────────────────────────────────────────────────
// ── MODE 2 : PILOTAGE ────────────────────────────────────────────────────────
// ────────────────────────────────────────────────────────────────────────────
class PilotageView extends StatelessWidget {
  const PilotageView({super.key});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const StatHeader(),
          const SizedBox(height: 24),
          Expanded(
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _joystickCard('THROTTLE / YAW', Colors.redAccent),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    _armButton(),
                    const SizedBox(height: 20),
                    const Text('FLIGHT MODE', style: TextStyle(color: Colors.white38, fontSize: 9, letterSpacing: 2)),
                    const SizedBox(height: 10),
                    _modeChip('STABILIZE',    Colors.cyanAccent),
                    const SizedBox(height: 6),
                    _modeChip('ALTITUDE HOLD', Colors.greenAccent),
                    const SizedBox(height: 6),
                    _modeChip('AUTO',          Colors.orangeAccent),
                  ],
                ),
                _joystickCard('PITCH / ROLL',   Colors.cyanAccent),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _joystickCard(String label, Color color) => NeonCard(
    child: SizedBox(
      width: 220,
      height: 240,
      child: Column(children: [
        Text(label, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold, letterSpacing: 1)),
        const SizedBox(height: 12),
        Expanded(child: CustomPaint(
          painter: _JoystickPainter(color: color),
          size: const Size(180, 180),
        )),
      ]),
    ),
  );

  Widget _armButton() => Container(
    padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
    decoration: BoxDecoration(
      color: Colors.redAccent.withValues(alpha: 0.12),
      borderRadius: BorderRadius.circular(10),
      border: Border.all(color: Colors.redAccent.withValues(alpha: 0.5)),
    ),
    child: const Text(
      'ARM',
      style: TextStyle(color: Colors.redAccent, fontWeight: FontWeight.bold, fontSize: 16, letterSpacing: 4),
    ),
  );

  Widget _modeChip(String label, Color color) => Container(
    width: 160,
    padding: const EdgeInsets.symmetric(vertical: 8),
    decoration: BoxDecoration(
      color: color.withValues(alpha: 0.05),
      borderRadius: BorderRadius.circular(6),
      border: Border.all(color: color.withValues(alpha: 0.2)),
    ),
    child: Text(
      label,
      textAlign: TextAlign.center,
      style: TextStyle(color: color.withValues(alpha: 0.7), fontSize: 10, letterSpacing: 1),
    ),
  );
}

class _JoystickPainter extends CustomPainter {
  final Color color;
  const _JoystickPainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final r  = math.min(cx, cy) - 6;

    // Outer ring
    canvas.drawCircle(Offset(cx, cy), r,
        Paint()
          ..style = PaintingStyle.stroke
          ..color = color.withValues(alpha: 0.25)
          ..strokeWidth = 2);

    // Inner ring (50%)
    canvas.drawCircle(Offset(cx, cy), r * 0.5,
        Paint()
          ..style = PaintingStyle.stroke
          ..color = color.withValues(alpha: 0.12)
          ..strokeWidth = 1);

    // Crosshair
    final gp = Paint()..color = color.withValues(alpha: 0.1)..strokeWidth = 1;
    canvas.drawLine(Offset(cx, cy - r), Offset(cx, cy + r), gp);
    canvas.drawLine(Offset(cx - r, cy), Offset(cx + r, cy), gp);

    // Center knob fill
    canvas.drawCircle(Offset(cx, cy), 16,
        Paint()..color = color.withValues(alpha: 0.12));
    // Center knob stroke
    canvas.drawCircle(Offset(cx, cy), 16,
        Paint()
          ..style = PaintingStyle.stroke
          ..color = color.withValues(alpha: 0.6)
          ..strokeWidth = 1.5);
  }

  @override
  bool shouldRepaint(_JoystickPainter old) => old.color != color;
}

// ────────────────────────────────────────────────────────────────────────────
// ── RealTimeValue — StatefulWidget avec mémoire ──────────────────────────────
// ────────────────────────────────────────────────────────────────────────────
class RealTimeValue extends StatefulWidget {
  final int    columnId;
  final String unit;
  final Color  color;
  final bool   isTimestamp;
  final bool   isPhase;

  const RealTimeValue({
    super.key,
    required this.columnId,
    required this.unit,
    required this.color,
    this.isTimestamp = false,
    this.isPhase     = false,
  });

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

  double? _extract(Map<String, dynamic> data) => switch (widget.columnId) {
    0  => (data['timestamp'] as num?)?.toDouble(),
    1  => (data['altitude']  as num?)?.toDouble(),
    2  => (data['speed']     as num?)?.toDouble(),
    5  => (data['az']        as num?)?.toDouble(),
    6  => (data['roll']      as num?)?.toDouble(),
    7  => (data['pitch']     as num?)?.toDouble(),
    8  => (data['yaw']       as num?)?.toDouble(),
    _  => null,
  };

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
          return Row(children: [
            _dot(connected), const SizedBox(width: 4),
            Flexible(child: Text(_lastPhase, style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: widget.color), overflow: TextOverflow.ellipsis)),
          ]);
        }

        if (widget.isTimestamp) {
          return Row(children: [
            _dot(connected), const SizedBox(width: 4),
            Text(_formatTs(_lastValue), style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: widget.color)),
          ]);
        }

        return Text(
          '${_lastValue.toStringAsFixed(1)}${widget.unit}',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: widget.color),
        );
      },
    );
  }

  Widget _dot(bool connected) => Container(
    width: 6, height: 6,
    decoration: BoxDecoration(
      shape: BoxShape.circle,
      color: connected ? Colors.greenAccent : Colors.redAccent,
      boxShadow: [BoxShadow(
        color: (connected ? Colors.greenAccent : Colors.redAccent).withValues(alpha: 0.6),
        blurRadius: 4,
      )],
    ),
  );
}

// ────────────────────────────────────────────────────────────────────────────
// ── RealTimeGraph — StatefulWidget optimisé ──────────────────────────────────
//   • fenêtre glissante (_maxGraphPoints)
//   • touchData désactivé (plus de bug au hover)
//   • clear sur Pause ou nouveau vol (timestamp reset)
// ────────────────────────────────────────────────────────────────────────────
class RealTimeGraph extends StatefulWidget {
  final List<int>   columnIds;
  final List<Color> colors;
  const RealTimeGraph({super.key, required this.columnIds, required this.colors});

  @override
  State<RealTimeGraph> createState() => _RealTimeGraphState();
}

class _RealTimeGraphState extends State<RealTimeGraph> {
  late List<List<FlSpot>> _allSpots;
  StreamSubscription<Map<String, dynamic>>? _sub;
  double _lastTs = -1;

  @override
  void initState() {
    super.initState();
    _allSpots = List.generate(widget.columnIds.length, (_) => []);

    // Clear quand on passe en PAUSE
    isLive.addListener(_onLiveChanged);

    _sub = flightStream.listen((data) {
      if (!isLive.value) return;

      final double x = (data['timestamp'] as num? ?? 0).toDouble();

      // Détection nouveau vol : le timestamp repart à 0
      if (_lastTs > 5.0 && x < _lastTs - 5.0) {
        setState(() {
          _allSpots = List.generate(widget.columnIds.length, (_) => []);
        });
      }
      _lastTs = x;

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
            // Fenêtre glissante
            if (_allSpots[i].length > _maxGraphPoints) {
              _allSpots[i].removeAt(0);
            }
          }
        }
      });
    });
  }

  void _onLiveChanged() {
    // Clear les courbes quand on met sur Pause
    if (!isLive.value) {
      setState(() {
        _allSpots = List.generate(widget.columnIds.length, (_) => []);
        _lastTs   = -1;
      });
    }
  }

  @override
  void dispose() {
    isLive.removeListener(_onLiveChanged);
    _sub?.cancel();
    super.dispose();
  }

  List<LineChartBarData> _buildBars() {
    return List.generate(widget.columnIds.length, (i) => LineChartBarData(
      spots:     _allSpots[i],
      isCurved:  true,
      color:     widget.colors[i],
      barWidth:  2.5,
      dotData:   const FlDotData(show: false),
      shadow:    Shadow(blurRadius: 8, color: widget.colors[i].withValues(alpha: 0.4)),
      belowBarData: BarAreaData(
        show:  i == 0,
        color: widget.colors[i].withValues(alpha: 0.05),
      ),
    ));
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<bool>(
      valueListenable: isLive,
      builder: (_, live, __) {
        if (!live) {
          return const Center(
            child: Text('SYSTEM PAUSED',
                style: TextStyle(color: Colors.white12, letterSpacing: 5, fontSize: 11)),
          );
        }

        final bars = _buildBars();
        if (bars.every((b) => b.spots.isEmpty)) {
          return const Center(child: CircularProgressIndicator(strokeWidth: 2));
        }

        return LineChart(
          duration: Duration.zero, // pas d'animation → plus fluide
          LineChartData(
            // ✅ Désactivation du touch → plus de bug au survol
            lineTouchData: const LineTouchData(enabled: false),
            gridData: FlGridData(
              show: true,
              getDrawingHorizontalLine: (_) =>
                  FlLine(color: Colors.white.withValues(alpha: 0.04), strokeWidth: 1),
              getDrawingVerticalLine: (_) =>
                  FlLine(color: Colors.white.withValues(alpha: 0.02), strokeWidth: 1),
            ),
            titlesData: FlTitlesData(
              show: true,
              topTitles:   const AxisTitles(),
              rightTitles: const AxisTitles(),
              bottomTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 24,
                  interval: 20,
                  getTitlesWidget: (v, _) => Text(
                    '${v.toInt()}s',
                    style: const TextStyle(color: Colors.white24, fontSize: 9),
                  ),
                ),
              ),
              leftTitles: AxisTitles(
                sideTitles: SideTitles(
                  showTitles: true,
                  reservedSize: 40,
                  getTitlesWidget: (value, meta) {
                    if (value == meta.max || value == meta.min) return const SizedBox();
                    return Text(
                      value.toStringAsFixed(1),
                      style: const TextStyle(color: Colors.white24, fontSize: 9),
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

// ── NeonCard ──────────────────────────────────────────────────────────────────
class NeonCard extends StatelessWidget {
  final Widget child;
  const NeonCard({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF0D0D1A),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white10),
      ),
      child: child,
    );
  }
}
import 'package:flutter/material.dart';
import 'package:frontend/widgets/neon_card.dart';
import 'package:frontend/widgets/flight_graph.dart';
import 'package:frontend/widgets/stat_header.dart';

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
              _graph('PROFIL DE MONTÉE (Altitude)', [1], [Colors.cyanAccent]),
              _graph('VITESSE DE VOL', [2], [Colors.redAccent]),
              _graph('ACCÉLÉRATION VERTICALE (AZ)', [5], [Colors.pinkAccent]),
              _graph('ORIENTATION (Roll, Pitch, Yaw)', [6, 7, 8], [Colors.blue, Colors.orange, Colors.greenAccent]),
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
                Expanded(child: Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12))),
                if (cols.length > 1) ...[
                  _legend('Roll', Colors.blue),
                  _legend('Pitch', Colors.orange),
                  _legend('Yaw', Colors.greenAccent),
                ],
              ],
            ),
            const SizedBox(height: 10),
            Expanded(child: RealTimeGraph(columnIds: cols, colors: colors)),
          ],
        ),
      ),
    );
  }

  Widget _legend(String name, Color col) => Padding(
    padding: const EdgeInsets.only(left: 12),
    child: Row(children: [Container(width: 8, height: 8, color: col), const SizedBox(width: 4), Text(name, style: const TextStyle(fontSize: 9, color: Colors.white54))]),
  );
}

import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:http/http.dart' as http;
import 'package:path_provider/path_provider.dart';
import 'package:frontend/widgets/neon_card.dart';
import 'package:frontend/widgets/flight_graph.dart';
import 'package:frontend/widgets/stat_header.dart';

class AnalyseView extends StatefulWidget {
  const AnalyseView({super.key});

  @override
  State<AnalyseView> createState() => _AnalyseViewState();
}

class _AnalyseViewState extends State<AnalyseView> {

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const StatHeader(),
          const SizedBox(height: 16),
          ElevatedButton.icon(
            onPressed: _downloadExcel,
            icon: const Icon(Icons.file_download),
            label: const Text('Télécharger Excel avec données et graphiques'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).primaryColor,
              foregroundColor: Colors.white,
            ),
          ),
          const SizedBox(height: 24),
          Wrap(
            spacing: 16,
            runSpacing: 16,
            alignment: WrapAlignment.center,
            children: [
              _graph('PROFIL DE MONTÉE (Altitude)', [1], [Colors.cyanAccent], 0),
              _graph('VITESSE DE VOL', [2], [Colors.redAccent], 1),
              _graph('ACCÉLÉRATION VERTICALE (AZ)', [5], [Colors.pinkAccent], 2),
              _graph('ORIENTATION (Roll, Pitch, Yaw)', [6, 7, 8], [Colors.blue, Colors.orange, Colors.greenAccent], 3),
            ],
          ),
        ],
      ),
    );
  }

  Widget _graph(String title, List<int> cols, List<Color> colors, int idx) {
    return SizedBox(
      width: 680,
      height: 280,
      child: NeonCard(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(child: Text(title, style: TextStyle(color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.white, fontWeight: FontWeight.bold, fontSize: 12))),
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
    child: Row(children: [Container(width: 8, height: 8, color: col), const SizedBox(width: 4), Text(name, style: TextStyle(fontSize: 9, color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7) ?? Colors.white54))]),
  );

  Future<void> _downloadExcel() async {
    try {
      final response = await http.get(Uri.parse('http://127.0.0.1:8000/download-excel'));
      if (response.statusCode == 200) {
        final dir = await getApplicationDocumentsDirectory();
        final file = File('${dir.path}/flight_data.xlsx');
        await file.writeAsBytes(response.bodyBytes);
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Fichier Excel téléchargé: ${file.path}')));
      } else {
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Erreur lors du téléchargement')));
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur: $e')));
    }
  }
}

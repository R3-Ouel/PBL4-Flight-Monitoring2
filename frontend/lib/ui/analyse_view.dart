import 'dart:io';
import 'dart:ui' as ui;

import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
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
  late final List<GlobalKey> _graphKeys;

  @override
  void initState() {
    super.initState();
    _graphKeys = List.generate(4, (_) => GlobalKey());
  }

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
    final key = _graphKeys[idx];
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
                const SizedBox(width: 8),
                IconButton(
                  icon: const Icon(Icons.file_download, size: 18),
                  color: Colors.white54,
                  tooltip: 'Télécharger le graphique',
                  onPressed: () => _saveGraph(idx, title),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Expanded(child: RepaintBoundary(key: key, child: RealTimeGraph(columnIds: cols, colors: colors))),
          ],
        ),
      ),
    );
  }

  Widget _legend(String name, Color col) => Padding(
    padding: const EdgeInsets.only(left: 12),
    child: Row(children: [Container(width: 8, height: 8, color: col), const SizedBox(width: 4), Text(name, style: TextStyle(fontSize: 9, color: Theme.of(context).textTheme.bodySmall?.color?.withOpacity(0.7) ?? Colors.white54))]),
  );

  Future<void> _saveGraph(int idx, String title) async {
    try {
      final key = _graphKeys[idx];
      final boundary = key.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Impossible de capturer le graphique')));
        return;
      }

      final ui.Image image = await boundary.toImage(pixelRatio: 3.0);
      final byteData = await image.toByteData(format: ui.ImageByteFormat.png);
      if (byteData == null) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Erreur lors de la capture')));
        return;
      }
      final bytes = byteData.buffer.asUint8List();

      final dir = await getApplicationDocumentsDirectory();
      final graphsDir = Directory('${dir.path}/graphs');
      if (!await graphsDir.exists()) await graphsDir.create(recursive: true);

      final base = title.toLowerCase().replaceAll(RegExp(r'[^a-z0-9]+'), '_').replaceAll(RegExp(r'_+'), '_').replaceAll(RegExp(r'^_|_$'), '');
      int fileIndex = 1;
      String fileName;
      do {
        final idxStr = fileIndex.toString().padLeft(3, '0');
        fileName = '${base}_$idxStr.png';
        fileIndex++;
      } while (await File('${graphsDir.path}/$fileName').exists());

      final file = File('${graphsDir.path}/$fileName');
      await file.writeAsBytes(bytes);

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Graphique sauvegardé: ${file.path}')));
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Erreur : $e')));
    }
  }
}

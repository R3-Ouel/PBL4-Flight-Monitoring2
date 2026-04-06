import 'dart:async';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

const String _wsUrl = 'ws://127.0.0.1:8000/ws/flight-data';

/// Global live toggles used across the UI
final ValueNotifier<bool> isLive = ValueNotifier<bool>(true);
final ValueNotifier<int> navMode = ValueNotifier<int>(0); // 0=Analyse,1=Navigation,2=Pilotage

/// FlightService: connects to backend WebSocket and exposes a broadcast stream
class FlightService {
  final _controller = StreamController<Map<String, dynamic>>.broadcast();
  final _bufferController = StreamController<void>.broadcast();
  final Map<String, List<List<double>>> _buffers = {};
  static const int _maxBufferPoints = 600;
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
            final normalized = {
              'timestamp': (raw['timestamp_ms'] ?? 0) / 1000.0,
              'altitude': (raw['altitude'] ?? 0).toDouble(),
              'speed': (raw['vitesse'] ?? raw['speed'] ?? 0).toDouble(),
              'ax': (raw['ax'] ?? 0).toDouble(),
              'ay': (raw['ay'] ?? 0).toDouble(),
              'az': (raw['az'] ?? 0).toDouble(),
              'roll': (raw['roll'] ?? 0).toDouble(),
              'pitch': (raw['pitch'] ?? 0).toDouble(),
              'yaw': (raw['yaw'] ?? 0).toDouble(),
              'phase': raw['phase'] ?? '',
              'flight_id': raw['flight_id'] ?? null,
            };

            // publish to consumers
            _controller.add(normalized);

            // append to internal buffers when Live is enabled
            _appendToBuffers(normalized);
          } catch (_) {}
        },
        onDone: () {
          if (!_disposed) Future.delayed(const Duration(seconds: 2), _connect);
        },
        onError: (_) {
          if (!_disposed) Future.delayed(const Duration(seconds: 2), _connect);
        },
        cancelOnError: false,
      );
    } catch (_) {
      if (!_disposed) Future.delayed(const Duration(seconds: 2), _connect);
    }
  }

  Stream<Map<String, dynamic>> get stream => _controller.stream;

  /// Stream that notifies when internal buffers are updated.
  Stream<void> get bufferStream => _bufferController.stream;

  /// Return a snapshot (immutable) of the buffer for a given key.
  List<List<double>> getBufferForKey(String key) => List.unmodifiable(_buffers[key] ?? []);

  void dispose() {
    _disposed = true;
    _channel?.sink.close();
    _controller.close();
    _bufferController.close();
  }

  void _appendToBuffers(Map<String, dynamic> data) {
    if (!isLive.value) return;
    final ts = (data['timestamp'] as num? ?? 0).toDouble();
    final keys = ['altitude', 'speed', 'az', 'roll', 'pitch', 'yaw'];
    var changed = false;
    for (final k in keys) {
      final v = (data[k] as num?)?.toDouble();
      if (v == null) continue;
      final buf = _buffers.putIfAbsent(k, () => <List<double>>[]);
      buf.add([ts, v]);
      if (buf.length > _maxBufferPoints) buf.removeAt(0);
      changed = true;
    }
    if (changed) {
      try {
        _bufferController.add(null);
      } catch (_) {}
    }
  }
}

final FlightService _flightService = FlightService();
Stream<Map<String, dynamic>> get flightStream => _flightService.stream;
Stream<void> get bufferStream => _flightService.bufferStream;
List<List<double>> getBufferForKey(String key) => _flightService.getBufferForKey(key);

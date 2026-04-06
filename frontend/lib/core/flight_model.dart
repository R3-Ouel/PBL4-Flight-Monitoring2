class FlightData {
  final double timestamp;
  final double altitude;
  final double speed;
  final double ax;
  final double ay;
  final double az;
  final double roll;
  final double pitch;
  final double yaw;
  final String phase;
  final String? flightId;

  FlightData({
    required this.timestamp,
    required this.altitude,
    required this.speed,
    required this.ax,
    required this.ay,
    required this.az,
    required this.roll,
    required this.pitch,
    required this.yaw,
    required this.phase,
    this.flightId,
  });

  factory FlightData.fromMap(Map<String, dynamic> m) {
    return FlightData(
      timestamp: (m['timestamp'] as num? ?? 0).toDouble(),
      altitude: (m['altitude'] as num? ?? 0).toDouble(),
      speed: (m['speed'] as num? ?? 0).toDouble(),
      ax: (m['ax'] as num? ?? 0).toDouble(),
      ay: (m['ay'] as num? ?? 0).toDouble(),
      az: (m['az'] as num? ?? 0).toDouble(),
      roll: (m['roll'] as num? ?? 0).toDouble(),
      pitch: (m['pitch'] as num? ?? 0).toDouble(),
      yaw: (m['yaw'] as num? ?? 0).toDouble(),
      phase: (m['phase'] as String? ?? ''),
      flightId: m['flight_id'] as String?,
    );
  }

  Map<String, dynamic> toMap() => {
        'timestamp': timestamp,
        'altitude': altitude,
        'speed': speed,
        'ax': ax,
        'ay': ay,
        'az': az,
        'roll': roll,
        'pitch': pitch,
        'yaw': yaw,
        'phase': phase,
        'flight_id': flightId,
      };
}

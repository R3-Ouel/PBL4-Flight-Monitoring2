from dronekit import connect, LocationGlobalRelative, VehicleMode, mavutil
from dronekit_sitl import SITL
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from math import radians, degrees
from time import sleep, time
import threading
import requests
import sys


##########################################################################
# MISSION PLANNER / SITL - Mode automatique
# Ce fichier lance SITL (ou se connecte à un autopilot si demandé),
# exécute une mission automatique (waypoints autour du home) et
# poste la télémétrie MAVLink vers FastAPI `/push` en arrière-plan.
##########################################################################


def lancer_sitl_propre(lat=-4.455742280012469, lon=15.288173956348162, alt=584, heading=0, instance=2, speedup=1):
    """
    Lance SITL aux coordonnées fournies (non-interactif).
    Retourne (vehicle, sitl).
    """
    print("\n" + "="*60)
    print("PREPARATION DU SIMULATEUR")
    print("="*60 + "\n")

    sitl = SITL()
    sitl.download('copter', '3.3', verbose=True)
    sitl_args = [f'--home={lat},{lon},0,{heading}']
    sitl.launch(sitl_args, await_ready=True, verbose=True)

    print("Simulateur lancé. Attente de stabilisation...")
    sleep(5)

    # Connexion au véhicule SITL
    vehicle = connect('tcp:127.0.0.1:5760', wait_ready=True, timeout=30)
    print("Connecté au simulateur SITL")
    return vehicle, sitl


def fermer_sitl_propre2(vehicle, sitl, max_retries=3):
    print("\n" + "="*60)
    print("ARRÊT PROPRE DU SYSTÈME")
    print("="*60 + "\n")

    success = True
    # Attendre désarmement si nécessaire
    try:
        for i in range(10):
            if not getattr(vehicle, 'armed', False):
                break
            print(f"Attente désarmement... {i+1}/10", end='\r')
            sleep(1)
    except Exception:
        pass

    # fermer vehicle
    try:
        vehicle.close()
    except Exception:
        pass

    # arrêter sitl
    try:
        sitl.stop()
    except Exception:
        pass

    print("Simulateur et véhicule fermés")
    return success


def connecter_drone(connection_string="tcp:127.0.0.1:5762"):
    print("Connexion à autopilot externe...")
    vehicle = connect(connection_string, wait_ready=True)
    print("Connexion réussie !")
    return vehicle


def fermer_sitl_propre1(vehicle):
    try:
        vehicle.close()
    except Exception:
        pass


def start_telemetry_sender(vehicle, endpoint='http://127.0.0.1:8000/push', interval=0.5, flight_id='SITL_MISSION'):
    """Démarre un thread qui lit les données MAVLink via DroneKit et POST sur /push."""
    stop_event = threading.Event()

    def _sender():
        # keep previous altitude/timestamps to compute vertical speed/acceleration fallback
        last_alt = None
        last_ts = None
        last_vz = None
        while not stop_event.is_set():
            try:
                ts_ms = int(time() * 1000)
                cur_ts = time()
                try:
                    alt = float(vehicle.location.global_relative_frame.alt)
                except Exception:
                    alt = 0.0
                # compute vertical speed (vz) as fallback: m/s
                vz = None
                dt = None
                if last_ts is not None:
                    dt = cur_ts - last_ts
                    if dt and dt > 0:
                        try:
                            vz = (alt - (last_alt if last_alt is not None else alt)) / dt
                        except Exception:
                            vz = None
                try:
                    speed = float(vehicle.groundspeed) if vehicle.groundspeed is not None else (float(vehicle.airspeed) if vehicle.airspeed is not None else 0.0)
                except Exception:
                    speed = 0.0
                try:
                    att = vehicle.attitude
                    roll = degrees(att.roll) if hasattr(att, 'roll') and att.roll is not None else 0.0
                    pitch = degrees(att.pitch) if hasattr(att, 'pitch') and att.pitch is not None else 0.0
                    yaw = degrees(att.yaw) if hasattr(att, 'yaw') and att.yaw is not None else (getattr(vehicle, 'heading', 0) or 0.0)
                except Exception:
                    roll = pitch = yaw = 0.0
                try:
                    raw = vehicle.raw_imu
                    raw_x = getattr(raw, 'xacc', None)
                    raw_y = getattr(raw, 'yacc', None)
                    raw_z = getattr(raw, 'zacc', None)
                    ax = (raw_x / 1000.0) if raw_x is not None else 0.0
                    ay = (raw_y / 1000.0) if raw_y is not None else 0.0
                    # prefer IMU zacc when available, otherwise estimate from vz derivative
                    if raw_z is not None:
                        az = raw_z / 1000.0
                    else:
                        if last_vz is not None and vz is not None and dt and dt > 0:
                            az = (vz - last_vz) / dt
                        else:
                            az = 0.0
                except Exception:
                    ax = ay = az = 0.0

                payload = {
                    'flight_id': flight_id,
                    'timestamp_ms': ts_ms,
                    'altitude': round(float(alt), 2),
                    'vitesse': round(float(speed), 2),
                    'ax': round(float(ax), 2),
                    'ay': round(float(ay), 2),
                    'az': round(float(az), 2),
                    'roll': round(float(roll), 2),
                    'pitch': round(float(pitch), 2),
                    'yaw': round(float(yaw), 2),
                    'phase': getattr(vehicle.mode, 'name', '') if hasattr(vehicle, 'mode') else '',
                    # New fields
                    'latitude': float(getattr(vehicle.location.global_relative_frame, 'lat', 0) or 0),
                    'longitude': float(getattr(vehicle.location.global_relative_frame, 'lon', 0) or 0),
                    # expose battery using English key for backend compatibility; keep French key for backwards compatibility
                    'battery': float(getattr(vehicle, 'battery', {}).level if getattr(vehicle, 'battery', None) and getattr(vehicle.battery, 'level', None) is not None else 0),
                    'batterie': float(getattr(vehicle, 'battery', {}).level if getattr(vehicle, 'battery', None) and getattr(vehicle.battery, 'level', None) is not None else 0),
                }

                try:
                    requests.post(endpoint, json=payload, timeout=1)
                except Exception:
                    pass
                # update last values for next iteration
                try:
                    last_alt = alt
                    last_ts = cur_ts
                    if vz is not None:
                        last_vz = vz
                except Exception:
                    pass
            except Exception:
                pass
            stop_event.wait(interval)

    t = threading.Thread(target=_sender, daemon=True)
    t.start()
    return stop_event, t


def define_auto_mission_from_vehicle(vehicle, altitude=15, speed=5, n_points=4, radius=40):
    try:
        home_lat = float(vehicle.location.global_relative_frame.lat)
        home_lon = float(vehicle.location.global_relative_frame.lon)
    except Exception:
        home_lat, home_lon = -4.455742280012469, 15.288173956348162

    points = []
    for i in range(n_points):
        bearing = i * (360.0 / n_points)
        dest = geodesic(meters=radius).destination((home_lat, home_lon), bearing)
        lat_d = dest.latitude
        lon_d = dest.longitude
        points.append({'lat': lat_d, 'lon': lon_d, 'name': f'WP{i+1}', 'location': LocationGlobalRelative(lat_d, lon_d, altitude)})

    return altitude, speed, points, (home_lat, home_lon)


def arm_and_takeoff(vehicle, altitude: int):
    print("Préparation armement et décollage...")
    try:
        forcer_mode(vehicle)
    except Exception:
        pass
    vehicle.armed = True
    while not vehicle.armed:
        print("En attente armement...", end='\r')
        sleep(0.5)
    vehicle.simple_takeoff(altitude)
    while True:
        try:
            if vehicle.location.global_relative_frame.alt >= altitude * 0.95:
                break
        except Exception:
            pass
        sleep(0.5)
    print("Altitude cible atteinte")


def execute_mission(vehicle, points: list, speed: int, home_coords: tuple):
    print("Exécution mission automatique...")
    for i, pt in enumerate(points):
        vehicle.simple_goto(pt['location'], groundspeed=speed)
        print(f"Aller vers {pt['name']} ({pt['lat']:.6f},{pt['lon']:.6f})")
        while True:
            try:
                coords = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
                dist = geodesic(coords, (pt['lat'], pt['lon'])).meters
            except Exception:
                dist = 9999
            if dist < 2:
                print(f"Arrivé {pt['name']}")
                break
            sleep(1)
    print("Retour au home")
    try:
        vehicle.mode = forcer_mode(vehicle, 'RTL')
        dist = geodesic((vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon), home_coords).meters
        while dist > 2:
            sleep(1)
            dist = geodesic((vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon), home_coords).meters
            print(f"Distance restante : {dist:.1f} m")
    except Exception:
        pass


def forcer_mode(vehicle, mode: str = 'GUIDED'):
    modes = ['STABILIZE','ACRO','ALT_HOLD','AUTO','GUIDED','LOITER','RTL','CIRCLE','POSITION','LAND']
    try:
        idx = modes.index(mode)
    except ValueError:
        idx = modes.index('GUIDED')
    try:
        msg = vehicle.message_factory.set_mode_encode(0, mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, idx)
        vehicle.send_mavlink(msg)
        vehicle.flush()
    except Exception:
        pass
    try:
        vehicle.mode = VehicleMode(mode)
    except Exception:
        pass
    return vehicle.mode if hasattr(vehicle, 'mode') else None


def afficher_distance_et_temps(vehicle, target_coords: tuple, speed: int):
    try:
        coords_drone = (vehicle.location.global_relative_frame.lat, vehicle.location.global_relative_frame.lon)
        dist = geodesic(coords_drone, target_coords).meters
        print(f"Distance restante : {dist:.1f} m")
    except Exception:
        pass


def wait_until_landed(vehicle, timeout: int = 300, alt_threshold: float = 0.5) -> bool:
    """Bloque jusqu'à l'atterrissage (altitude < alt_threshold et désarmé) ou timeout.
    Retourne True si atterri, False si timeout.
    """
    start_t = time()
    try:
        while time() - start_t < timeout:
            try:
                alt = getattr(vehicle.location.global_relative_frame, 'alt', None)
                armed = getattr(vehicle, 'armed', False)
                if alt is not None:
                    print(f"Attente atterrissage... alt={alt:.2f} m, armed={armed}")
                    if alt <= alt_threshold and not armed:
                        print("Atterrissage détecté - drone posé et désarmé.")
                        return True
                else:
                    print(f"Attente atterrissage... armed={armed}")
                    if not armed:
                        print("Drone désarmé.")
                        return True
            except Exception as e:
                print("Erreur pendant attente atterrissage:", e)
            sleep(1)
    except Exception:
        pass
    print("Timeout waiting for landing.")
    return False


def main():
    # Mode par défaut: lancer SITL et exécuter une mission automatique
    use_connect = len(sys.argv) > 1 and sys.argv[1] in ('connect', 'external')
    sitl = None
    try:
        if use_connect:
            vehicle = connecter_drone()
        else:
            vehicle, sitl = lancer_sitl_propre()

        stop_event, thread = None, None
        try:
            stop_event, thread = start_telemetry_sender(vehicle, endpoint='http://127.0.0.1:8000/push', interval=0.5)
        except Exception:
            stop_event = None

        altitude, speed, points, home_coords = define_auto_mission_from_vehicle(vehicle, altitude=15, speed=5, n_points=4, radius=40)
        arm_and_takeoff(vehicle, altitude)
        execute_mission(vehicle, points, speed, home_coords)

    except KeyboardInterrupt:
        print("Mission interrompue par l'utilisateur")
    except Exception as e:
        print(f"Erreur: {e}")
    finally:
        try:
            if 'vehicle' in locals() and vehicle:
                try:
                    # Demander l'atterrissage puis attendre qu'il soit effectivement terminé
                    vehicle.mode = forcer_mode(vehicle, 'LAND')
                except Exception:
                    pass

                # Attendre l'atterrissage (altitude faible + désarmé) avant d'arrêter la télémétrie
                try:
                    wait_until_landed(vehicle, timeout=300, alt_threshold=0.5)
                except Exception:
                    pass

                # Stop telemetry sender only after landing
                if stop_event:
                    stop_event.set()

                if sitl:
                    # fermer proprement (fermer véhicule + arrêter sitl)
                    fermer_sitl_propre2(vehicle, sitl)
                else:
                    try:
                        vehicle.close()
                    except Exception:
                        pass
        except Exception:
            pass


if __name__ == "__main__":
    main()

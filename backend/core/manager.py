import os
import csv
import time
import threading
from pathlib import Path
from dotenv import load_dotenv

try:
    from supabase import create_client
except Exception:
    create_client = None


# Charger .env si présent
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = None
if create_client and SUPABASE_URL and SUPABASE_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print("Supabase client init failed:", e)


# Fichier CSV (backend/data/flight_data.csv)
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "flight_data.csv"
POS_PATH = DATA_DIR / "flight_data.pos"
CSV_HEADERS = [
    "timestamp",
    "altitude",
    "vitesse",
    "ax",
    "ay",
    "az",
    "roll",
    "pitch",
    "yaw",
    "latitude",
    "longitude",
    "battery",
    "phase",
]


_lock = threading.Lock()
_stop_event = None
_thread = None


def _ensure_csv_header():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        try:
            with open(CSV_PATH, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADERS)
        except Exception as e:
            print("Erreur création header CSV:", e)


def _load_last_pos() -> int:
    try:
        if POS_PATH.exists():
            text = POS_PATH.read_text().strip()
            return int(text) if text else 0
    except Exception:
        pass
    return 0


def _save_last_pos(n: int):
    try:
        POS_PATH.parent.mkdir(parents=True, exist_ok=True)
        POS_PATH.write_text(str(n))
    except Exception as e:
        print("Failed saving pos:", e)


def process_payload(payload: dict) -> bool:
    """Écrit la ligne dans le CSV uniquement (pas d'insertion Supabase ici).
    Cette opération est synchrone et doit être lancée dans un thread pour éviter de bloquer.
    """
    try:
        _ensure_csv_header()

        ts_ms = payload.get("timestamp_ms") or int(time.time() * 1000)
        try:
            timestamp = int(int(ts_ms) // 1000)
        except Exception:
            timestamp = int(time.time())

        row = [
            timestamp,
            payload.get("altitude", 0),
            payload.get("vitesse", 0),
            payload.get("ax", 0),
            payload.get("ay", 0),
            payload.get("az", 0),
            payload.get("roll", 0),
            payload.get("pitch", 0),
            payload.get("yaw", 0),
            payload.get("latitude", 0),
            payload.get("longitude", 0),
            payload.get("battery", 0),
            payload.get("phase", ""),
        ]

        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        return True
    except Exception as e:
        print("process_payload failed:", e)
        return False


def _read_new_rows(last_pos: int):
    rows = []
    new_pos = last_pos
    if not CSV_PATH.exists():
        return rows, new_pos
    try:
        with open(CSV_PATH, newline="") as f:
            reader = csv.DictReader(f)
            for idx, r in enumerate(reader, start=1):
                if idx > last_pos:
                    rows.append(r)
                    new_pos = idx
    except Exception as e:
        print("Erreur lecture CSV:", e)
    return rows, new_pos


def _rows_to_payloads(rows):
    payloads = []
    for r in rows:
        try:
            timestamp = int(float(r.get("timestamp", 0)))
            payload = {
                "flight_id": r.get("flight_id") or "CSV_IMPORT",
                "timestamp_ms": int(timestamp * 1000),
                "altitude": float(r.get("altitude", 0)),
                "vitesse": float(r.get("vitesse", 0)),
                "ax": float(r.get("ax", 0)),
                "ay": float(r.get("ay", 0)),
                "az": float(r.get("az", 0)),
                "roll": float(r.get("roll", 0)),
                "pitch": float(r.get("pitch", 0)),
                "yaw": float(r.get("yaw", 0)),
                "latitude": float(r.get("latitude", 0)),
                "longitude": float(r.get("longitude", 0)),
                "battery": float(r.get("battery", 0)),
                "phase": r.get("phase", ""),
            }
            payloads.append(payload)
        except Exception as e:
            print("Skipped row due to parse error:", e)
    return payloads


def _push_to_supabase(payloads) -> bool:
    if not supabase or not payloads:
        return False
    try:
        BATCH = 100
        for i in range(0, len(payloads), BATCH):
            batch = payloads[i : i + BATCH]
            supabase.table("telemetrie").insert(batch).execute()
        return True
    except Exception as e:
        print("Erreur insertion Supabase:", e)
        return False


def _pusher_loop(interval: int, stop_event: threading.Event):
    last_pos = _load_last_pos()
    while not stop_event.is_set():
        try:
            rows, new_pos = _read_new_rows(last_pos)
            if rows:
                payloads = _rows_to_payloads(rows)
                ok = _push_to_supabase(payloads)
                if ok:
                    last_pos = new_pos
                    _save_last_pos(last_pos)
        except Exception as e:
            print("Exception in pusher loop:", e)
        stop_event.wait(interval)


def start_csv_pusher(interval: int = 5):
    """Démarre un thread daemon qui pousse les lignes CSV vers Supabase toutes les `interval` secondes.
    Retourne `(stop_event, thread)`.
    """
    global _stop_event, _thread
    if _thread and _thread.is_alive():
        return _stop_event, _thread
    _stop_event = threading.Event()
    _thread = threading.Thread(target=_pusher_loop, args=(interval, _stop_event), daemon=True)
    _thread.start()
    return _stop_event, _thread


def stop_csv_pusher():
    global _stop_event
    if _stop_event:
        _stop_event.set()

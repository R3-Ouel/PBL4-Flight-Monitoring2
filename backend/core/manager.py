import os
import csv
import time
import re
import threading
import shutil
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
    "batterie",
    "phase",
]

SUPABASE_TABLE = "telemetrie"
SUPABASE_INSERT_COLUMNS = [
    "flight_id",
    "timestamp_ms",
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
    "batterie",
    "phase",
]


_lock = threading.Lock()
_stop_event = None
_thread = None
_disabled_supabase_columns = set()


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
            payload.get("batterie", 0),
            payload.get("phase", ""),
        ]

        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        # Also copy the updated CSV into the frontend assets so the Flutter app
        # can access the latest CSV file (useful for desktop/testing workflows).
        try:
            repo_root = BASE_DIR.parent
            frontend_assets = repo_root / "frontend" / "assets"
            frontend_assets_csv = frontend_assets / "flight_data.csv"
            frontend_root_csv = repo_root / "frontend" / "flight_data.csv"
            frontend_assets.mkdir(parents=True, exist_ok=True)
            shutil.copy2(CSV_PATH, frontend_assets_csv)
            shutil.copy2(CSV_PATH, frontend_root_csv)
        except Exception as e:
            print("Failed to copy CSV to frontend assets:", e)

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
                # Normalize CSV 'batterie' column to payload key 'batterie'
                "batterie": float(r.get("batterie", 0)),
                "phase": r.get("phase", ""),
            }
            payloads.append(payload)
        except Exception as e:
            print("Skipped row due to parse error:", e)
    return payloads


def _extract_missing_column(exc: Exception) -> str | None:
    """Extract a missing-column name from a PostgREST schema-cache error."""
    text = str(exc)
    match = re.search(r"Could not find the '([^']+)' column", text)
    if match:
        return match.group(1)
    return None


def _is_bigint_syntax_error(exc: Exception) -> bool:
    text = str(exc)
    return "invalid input syntax for type bigint" in text


def _disable_bigint_candidate_columns(batch) -> bool:
    """Disable likely bigint columns that are receiving decimal values.

    Without schema introspection, prefer dropping lower-priority optional numeric
    fields until the insert succeeds instead of blocking the whole CSV pusher.
    """
    candidate_order = [
        "batterie",
        "battery",
        "latitude",
        "longitude",
        "yaw",
        "pitch",
        "roll",
        "az",
        "ay",
        "ax",
        "vitesse",
        "altitude",
    ]

    for column in candidate_order:
        if column in _disabled_supabase_columns:
            continue

        has_numeric_value = False
        for item in batch:
            value = item.get(column)
            if value is None or value == "":
                continue
            try:
                float(value)
                has_numeric_value = True
                break
            except Exception:
                continue

        if has_numeric_value:
            _disabled_supabase_columns.add(column)
            print(
                f"Supabase column '{column}' appears incompatible with numeric payloads, "
                "disabling it for future inserts."
            )
            return True

    return False


def _sanitize_batch(batch):
    allowed_columns = [c for c in SUPABASE_INSERT_COLUMNS if c not in _disabled_supabase_columns]
    sanitized = []

    for item in batch:
        s = {}
        if "flight_id" in allowed_columns:
            s["flight_id"] = str(item.get("flight_id") or "CSV_IMPORT")
        if "timestamp_ms" in allowed_columns:
            try:
                ts_val = item.get("timestamp_ms", 0)
                s["timestamp_ms"] = int(float(ts_val))
            except Exception:
                s["timestamp_ms"] = 0

        numeric_columns = (
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
            "batterie",
        )
        for key in numeric_columns:
            if key not in allowed_columns:
                continue
            try:
                s[key] = float(item.get(key, 0) or 0)
            except Exception:
                s[key] = 0.0

        if "phase" in allowed_columns:
            s["phase"] = str(item.get("phase") or "")

        sanitized.append(s)

    return sanitized


def _push_to_supabase(payloads) -> bool:
    if not supabase or not payloads:
        return False
    try:
        BATCH = 100
        for i in range(0, len(payloads), BATCH):
            batch = payloads[i : i + BATCH]
            while True:
                sanitized = _sanitize_batch(batch)
                try:
                    supabase.table(SUPABASE_TABLE).insert(sanitized).execute()
                    break
                except Exception as e:
                    missing_column = _extract_missing_column(e)
                    if missing_column and missing_column not in _disabled_supabase_columns:
                        _disabled_supabase_columns.add(missing_column)
                        print(
                            f"Supabase column '{missing_column}' not found in '{SUPABASE_TABLE}', "
                            "disabling it for future inserts."
                        )
                        continue
                    if _is_bigint_syntax_error(e) and _disable_bigint_candidate_columns(batch):
                        continue

                    # Log sanitized payload for debugging
                    print("Supabase insert failed for batch (sanitized):", sanitized)
                    raise
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

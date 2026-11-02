#jo
import csv
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

#mm
import shutil

#jo
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WATCHLIST_FILE = DATA_DIR / "watchlist.csv"
REQUIRED_FIELDS = ["id", "title", "genre", "platform", "rating", "duration"]
FIELDS = REQUIRED_FIELDS + ["release_date"]

#jo
BACKUP_DIR = DATA_DIR / "backups"
MOVIES_CACHE_FILE = DATA_DIR / "movies_cache.json"

#mm
EXPORTS_DIR = Path(__file__).resolve().parent.parent / "exports"
REPORT_FIELDS = ["platforma", "liczba_filmow", "srednia_ocena", "najnizsza_ocena", "najwyzsza_ocena"]

#mm
def export_platform_report(rows: list) -> Path:
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report_path = EXPORTS_DIR / "raport_platform.csv"
    with open(report_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=REPORT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return report_path

#mm
def backup_watchlist(keep: int = 3) -> Path | None:
    if not WATCHLIST_FILE.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"watchlist_{stamp}.bak"
    shutil.copy2(WATCHLIST_FILE, backup_path)
    backups = sorted(BACKUP_DIR.glob("watchlist_*.bak"))
    while len(backups) > keep:
        oldest = backups.pop(0)
        oldest.unlink(missing_ok=True)
    return backup_path

#jo
def minutes_to_hours(minutes: int) -> str:
    return f"{minutes // 60}:{minutes % 60:02d}"

#jo
def hours_to_minutes(text: str) -> int:
    if ":" in text:
        hours, minutes = text.split(":")
        return int(hours) * 60 + int(minutes)
    return int(text)

#jo (edit:mm)
def save_watchlist(items_list: list) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    backup_watchlist()
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=DATA_DIR,
        prefix="watchlist_tmp_",
        suffix=".csv",
        delete=False,
        newline="",
        encoding="utf-8",
    ) as tmp:
        writer = csv.DictWriter(tmp, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        for item in items_list:
            writer.writerow({**item, "duration": minutes_to_hours(item["duration"])})
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = tmp.name
    os.replace(temp_path, WATCHLIST_FILE)

#jo (edit:mm)
def read_watchlist_file(path: Path) -> list:
    with open(path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None or not set(REQUIRED_FIELDS).issubset(reader.fieldnames):
            raise ValueError("Zły nagłówek pliku")
        rows = list(reader)
    watchlist = []
    for row in rows:
        watchlist.append({
            "id": int(row["id"]),
            "title": row["title"],
            "genre": row["genre"],
            "platform": row["platform"],
            "rating": float(row["rating"]),
            "duration": hours_to_minutes(row["duration"]),
            "release_date": row.get("release_date") or "-",
        })
    return watchlist

#jo
READ_ERRORS = (KeyError, ValueError, TypeError, csv.Error, UnicodeDecodeError)

#jo
def repair_watchlist() -> list:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    corrupted_path = DATA_DIR / f"corrupted_{stamp}.csv"
    os.replace(WATCHLIST_FILE, corrupted_path)
    print(f"[OSTRZEŻENIE] Plik {WATCHLIST_FILE.name} jest uszkodzony, przeniesiono go do {corrupted_path.name}.")
    for backup_path in sorted(BACKUP_DIR.glob("watchlist_*.bak"), reverse=True):
        try:
            watchlist = read_watchlist_file(backup_path)
        except READ_ERRORS:
            continue
        save_watchlist(watchlist)
        print(f"Przywrócono watchlistę z kopii {backup_path.name}.")
        return watchlist
    print("Brak dobrej kopii zapasowej, watchlista zaczyna się od nowa.")
    save_watchlist([])
    return []

#jo
def load_watchlist() -> list:
    try:
        return read_watchlist_file(WATCHLIST_FILE)
    except FileNotFoundError:
        save_watchlist([])
        return []
    except READ_ERRORS:
        return repair_watchlist()

#jo
def backup_movies_cache(keep: int = 3) -> Path | None:
    if not MOVIES_CACHE_FILE.exists():
        return None
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = BACKUP_DIR / f"movies_cache_{stamp}.bak"
    shutil.copy2(MOVIES_CACHE_FILE, backup_path)
    backups = sorted(BACKUP_DIR.glob("movies_cache_*.bak"))
    while len(backups) > keep:
        oldest = backups.pop(0)
        oldest.unlink(missing_ok=True)
    return backup_path

#jo
def save_movies_cache(movies: list) -> None:
    text = json.dumps(movies, indent=4, ensure_ascii=False)
    if MOVIES_CACHE_FILE.exists() and MOVIES_CACHE_FILE.read_text(encoding="utf-8") == text:
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    backup_movies_cache()
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=DATA_DIR,
        prefix="movies_tmp_",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        tmp.write(text)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = tmp.name
    os.replace(temp_path, MOVIES_CACHE_FILE)

#jo
CACHE_ERRORS = (ValueError, UnicodeDecodeError)

#jo
def read_movies_cache(path: Path) -> list:
    with open(path, mode="r", encoding="utf-8") as file:
        movies = json.load(file)
    if not isinstance(movies, list):
        raise ValueError("Zły format kopii filmów")
    return movies

#jo
def repair_movies_cache() -> list:
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    corrupted_path = DATA_DIR / f"corrupted_movies_{stamp}.json"
    os.replace(MOVIES_CACHE_FILE, corrupted_path)
    print(f"[OSTRZEŻENIE] Plik {MOVIES_CACHE_FILE.name} jest uszkodzony, przeniesiono go do {corrupted_path.name}.")
    for backup_path in sorted(BACKUP_DIR.glob("movies_cache_*.bak"), reverse=True):
        try:
            movies = read_movies_cache(backup_path)
        except CACHE_ERRORS:
            continue
        save_movies_cache(movies)
        print(f"Przywrócono filmy z kopii {backup_path.name}.")
        return movies
    print("Brak dobrej kopii zapasowej filmów.")
    return []

#jo
def load_movies_cache() -> list:
    try:
        return read_movies_cache(MOVIES_CACHE_FILE)
    except FileNotFoundError:
        print("Brak zapisanej kopii filmów. Połącz się z internetem, żeby ją pobrać.")
        return []
    except CACHE_ERRORS:
        return repair_movies_cache()

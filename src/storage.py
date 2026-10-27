#jo
import csv
import os
import tempfile
from datetime import datetime
from pathlib import Path

#jo
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WATCHLIST_FILE = DATA_DIR / "watchlist.csv"
FIELDS = ["id", "title", "genre", "platform", "rating", "duration"]

#jo
BACKUP_DIR = DATA_DIR / "backups"

#jo
def save_watchlist(items_list: list) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
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
        writer.writerows(items_list)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = tmp.name
    os.replace(temp_path, WATCHLIST_FILE)

#jo
def read_watchlist_file(path: Path) -> list:
    with open(path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames != FIELDS:
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
            "duration": int(row["duration"]),
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

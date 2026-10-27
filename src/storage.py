#jo
import csv
import os
import tempfile
from pathlib import Path

#jo
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WATCHLIST_FILE = DATA_DIR / "watchlist.csv"
FIELDS = ["id", "title", "genre", "platform", "rating", "duration"]

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
def load_watchlist() -> list:
    try:
        with open(WATCHLIST_FILE, mode="r", newline="", encoding="utf-8") as file:
            rows = list(csv.DictReader(file))
    except FileNotFoundError:
        save_watchlist([])
        return []
    watchlist = []
    try:
        for row in rows:
            watchlist.append({
                "id": int(row["id"]),
                "title": row["title"],
                "genre": row["genre"],
                "platform": row["platform"],
                "rating": float(row["rating"]),
                "duration": int(row["duration"]),
            })
    except (KeyError, ValueError, TypeError):
        print(f"Błąd: Plik {WATCHLIST_FILE.name} jest uszkodzony, watchlista zaczyna się od nowa.")
        return []
    return watchlist

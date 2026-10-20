#jo
import csv
from pathlib import Path

#jo
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WATCHLIST_FILE = DATA_DIR / "watchlist.csv"
FIELDS = ["id", "title", "genre", "platform", "rating", "duration"]

#jo
def save_watchlist(items_list: list) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(WATCHLIST_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(items_list)

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

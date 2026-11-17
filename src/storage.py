#jo
import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

#mm
import shutil
from models import Watchlist

#jo
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"

#jo
BACKUP_DIR = DATA_DIR / "backups"
MOVIES_CACHE_FILE = DATA_DIR / "movies_cache.json"
PENDING_MOVIES_FILE = DATA_DIR / "pending_movies.json"

#jo
def hours_to_minutes(text: str) -> int:
    if ":" in text:
        hours, minutes = text.split(":")
        return int(hours) * 60 + int(minutes)
    return int(text)

#mm
def read_watchlist_file(path: Path) -> Watchlist:
    with open(path, mode="r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict) or not isinstance(data.get("items"), list):
        raise ValueError("Zły format watchlisty")
    for item in data["items"]:
        item["duration"] = hours_to_minutes(str(item["duration"]))
    return Watchlist.from_dict(data)

#jo (edit:mm)
READ_ERRORS = (KeyError, ValueError, TypeError, AttributeError, UnicodeDecodeError)

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

#jo
def get_cache_update_time() -> str:
    if not MOVIES_CACHE_FILE.exists():
        return "brak"
    mtime = MOVIES_CACHE_FILE.stat().st_mtime
    return datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")

#jo
def load_pending_movies() -> list:
    if not PENDING_MOVIES_FILE.exists():
        return []
    try:
        with open(PENDING_MOVIES_FILE, mode="r", encoding="utf-8") as file:
            data = json.load(file)
            return data if isinstance(data, list) else []
    except (ValueError, UnicodeDecodeError):
        return []

#jo
def save_pending_movies(movies: list) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w",
        dir=DATA_DIR,
        prefix="pending_tmp_",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as tmp:
        json.dump(movies, tmp, indent=4, ensure_ascii=False)
        tmp.flush()
        os.fsync(tmp.fileno())
        temp_path = tmp.name
    os.replace(temp_path, PENDING_MOVIES_FILE)

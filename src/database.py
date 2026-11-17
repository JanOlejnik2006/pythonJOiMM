#jo
import sqlite3
from pathlib import Path

#jo
DB_FILE = Path(__file__).resolve().parent.parent / "data" / "cinestream.db"

#jo
DDL_WATCHLISTS = """
CREATE TABLE IF NOT EXISTS watchlists (
    watchlist_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""

#jo
DDL_MEDIA_ITEMS = """
CREATE TABLE IF NOT EXISTS media_items (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    watchlist_id INTEGER NOT NULL,
    media_id INTEGER NOT NULL,
    type TEXT NOT NULL DEFAULT 'movie',
    title TEXT NOT NULL,
    genre TEXT NOT NULL,
    platform TEXT NOT NULL,
    release_date TEXT NOT NULL DEFAULT '-',
    year INTEGER,
    rating REAL CHECK (rating BETWEEN 1.0 AND 10.0),
    is_watched INTEGER NOT NULL DEFAULT 0 CHECK (is_watched IN (0, 1)),
    duration_min INTEGER NOT NULL CHECK (duration_min > 0),
    director TEXT,
    seasons INTEGER,
    episodes_per_season INTEGER,
    minutes_per_episode INTEGER,
    UNIQUE (watchlist_id, media_id),
    FOREIGN KEY (watchlist_id) REFERENCES watchlists(watchlist_id) ON DELETE CASCADE
);
"""

#jo
def get_connection(db_path: str | Path = DB_FILE) -> sqlite3.Connection:
    """Fabryka połączeń: włącza klucze obce i wyniki jako sqlite3.Row (dostęp po nazwie kolumny)."""
    if db_path != ":memory:":
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

#jo
def init_db(conn: sqlite3.Connection) -> None:
    """Zakłada tabele, jeśli jeszcze ich nie ma (bezpieczne przy każdym starcie)."""
    with conn:
        conn.execute(DDL_WATCHLISTS)
        conn.execute(DDL_MEDIA_ITEMS)

#jo
import sqlite3
from pathlib import Path
from models import MediaTitle, media_from_dict

#jo
from storage import READ_ERRORS, WATCHLIST_FILE, read_watchlist_file

#mm
from datetime import datetime
from models import Watchlist

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
ALLOWED_SORT_COLUMNS = {"title", "rating", "duration_min", "year"}

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

#jo
def media_to_row(media: MediaTitle, watchlist_id: int) -> dict:
    """Obiekt -> wiersz tabeli media_items (bool na 0/1, czas zawsze w minutach)."""
    data = media.to_dict()
    return {
        "watchlist_id": watchlist_id,
        "media_id": data["id"],
        "type": data["type"],
        "title": data["title"],
        "genre": data["genre"],
        "platform": data["platform"],
        "release_date": data["release_date"],
        "year": media.year,
        "rating": data["rating"],
        "is_watched": int(data["is_watched"]),
        "duration_min": media.runtime_minutes(),
        "director": data.get("director"),
        "seasons": data.get("seasons"),
        "episodes_per_season": data.get("episodes_per_season"),
        "minutes_per_episode": data.get("minutes_per_episode"),
    }

#jo
def row_to_media(row: sqlite3.Row) -> MediaTitle:
    """Wiersz tabeli -> obiekt przez fabrykę z Zadania 3 (puste kolumny pomijamy)."""
    data = {key: value for key, value in dict(row).items() if value is not None}
    data["id"] = data["media_id"]
    data["duration"] = data["duration_min"]
    data["is_watched"] = bool(data["is_watched"])
    return media_from_dict(data)

#mm
INSERT_ITEM = """
INSERT INTO media_items (
    watchlist_id, media_id, type, title, genre, platform, release_date, year, rating,
    is_watched, duration_min, director, seasons, episodes_per_season, minutes_per_episode
) VALUES (
    :watchlist_id, :media_id, :type, :title, :genre, :platform, :release_date, :year, :rating,
    :is_watched, :duration_min, :director, :seasons, :episodes_per_season, :minutes_per_episode
);
"""

#mm
class WatchlistRepository:
    """Repozytorium: cały SQL watchlisty w jednym miejscu, menu i klasy nie piszą zapytań."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn
        init_db(conn)

    def count_watchlists(self) -> int:
        return self._conn.execute("SELECT COUNT(*) FROM watchlists;").fetchone()[0]

    def save_watchlist(self, watchlist: Watchlist) -> int:
        """Transakcja: watchlista i wszystkie jej pozycje zapisują się razem albo wcale."""
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self._conn:
            cur = self._conn.execute(
                "INSERT INTO watchlists (name, created_at) VALUES (?, ?);",
                (watchlist.name, created_at),
            )
            watchlist_id = cur.lastrowid
            rows = [media_to_row(media, watchlist_id) for media in watchlist.items]
            self._conn.executemany(INSERT_ITEM, rows)
        return watchlist_id

    def load_watchlist(self, watchlist_id: int) -> Watchlist | None:
        row = self._conn.execute(
            "SELECT name FROM watchlists WHERE watchlist_id = ?;", (watchlist_id,)
        ).fetchone()
        if row is None:
            return None
        items = self._conn.execute(
            "SELECT * FROM media_items WHERE watchlist_id = ? ORDER BY item_id;", (watchlist_id,)
        ).fetchall()
        return Watchlist(row["name"], [row_to_media(item) for item in items])

    #jo
    def search_items(
        self,
        phrase: str = "",
        min_rating: float | None = None,
        is_watched: bool | None = None,
        sort_by: str = "title",
    ) -> list[MediaTitle]:
        """Filtr: fragment tytułu (LIKE), minimalna ocena i status. Kolumna sortowania tylko z białej listy."""
        if sort_by not in ALLOWED_SORT_COLUMNS:
            raise ValueError(f"Niedozwolona kolumna sortowania: {sort_by}")
        sql = (
            "SELECT * FROM media_items "
            "WHERE title LIKE :pattern "
            "AND (:min_rating IS NULL OR rating >= :min_rating) "
            "AND (:is_watched IS NULL OR is_watched = :is_watched) "
            f"ORDER BY {sort_by} ASC;"
        )
        params = {
            "pattern": f"%{phrase}%",
            "min_rating": min_rating,
            "is_watched": None if is_watched is None else int(is_watched),
        }
        rows = self._conn.execute(sql, params).fetchall()
        return [row_to_media(row) for row in rows]

    def first_watchlist_id(self) -> int | None:
        row = self._conn.execute("SELECT watchlist_id FROM watchlists ORDER BY watchlist_id LIMIT 1;").fetchone()
        return row["watchlist_id"] if row is not None else None

    def add_item(self, watchlist_id: int, media: MediaTitle) -> None:
        with self._conn:
            self._conn.execute(INSERT_ITEM, media_to_row(media, watchlist_id))

    def remove_item(self, watchlist_id: int, media_id: int) -> None:
        with self._conn:
            self._conn.execute(
                "DELETE FROM media_items WHERE watchlist_id = ? AND media_id = ?;", (watchlist_id, media_id)
            )

    def update_rating(self, watchlist_id: int, media: MediaTitle) -> None:
        with self._conn:
            self._conn.execute(
                "UPDATE media_items SET is_watched = ?, rating = ? WHERE watchlist_id = ? AND media_id = ?;",
                (int(media.is_watched), media.rating, watchlist_id, media.title_id),
            )

    def delete_watchlist(self, watchlist_id: int) -> None:
        """Usuwa watchlistę, a pozycje znikają same dzięki ON DELETE CASCADE."""
        with self._conn:
            self._conn.execute("DELETE FROM watchlists WHERE watchlist_id = ?;", (watchlist_id,))

    def count_items(self, watchlist_id: int) -> int:
        return self._conn.execute(
            "SELECT COUNT(*) FROM media_items WHERE watchlist_id = ?;", (watchlist_id,)
        ).fetchone()[0]

    #jo
    def move_item(self, media: MediaTitle, from_id: int, to_id: int) -> None:
        """Transakcja w dwóch krokach: usuń z jednej listy, dodaj do drugiej. Błąd w kroku 2 cofa krok 1 (ROLLBACK)."""
        with self._conn:
            cur = self._conn.execute(
                "DELETE FROM media_items WHERE watchlist_id = ? AND media_id = ?;",
                (from_id, media.title_id),
            )
            if cur.rowcount == 0:
                raise ValueError(f"Na liście {from_id} nie ma pozycji o ID {media.title_id}.")
            self._conn.execute(INSERT_ITEM, media_to_row(media, to_id))

    #mm
    def watchlist_report(self, min_titles: int = 0) -> list[dict]:
        """Raport list: LEFT JOIN pokazuje też puste listy, COALESCE zamienia NULL na 0, HAVING to próg."""
        sql = """
        SELECT
            w.watchlist_id,
            w.name,
            COUNT(m.item_id) AS titles,
            COALESCE(SUM(m.duration_min), 0) AS total_min,
            COALESCE(ROUND(AVG(m.rating), 2), 0.0) AS avg_rating
        FROM watchlists AS w
        LEFT JOIN media_items AS m ON w.watchlist_id = m.watchlist_id
        GROUP BY w.watchlist_id, w.name
        HAVING COUNT(m.item_id) >= ?
        ORDER BY total_min DESC;
        """
        rows = self._conn.execute(sql, (min_titles,)).fetchall()
        return [dict(row) for row in rows]

    #mm
    def platform_report(self, watchlist_id: int, min_titles: int = 1) -> list[dict]:
        """Raport platform jednej listy: JOIN + GROUP BY po platformie, HAVING odrzuca małe grupy."""
        sql = """
        SELECT
            m.platform,
            COUNT(m.item_id) AS titles,
            COALESCE(SUM(m.duration_min), 0) AS total_min,
            COALESCE(SUM(m.is_watched), 0) AS watched
        FROM watchlists AS w
        JOIN media_items AS m ON w.watchlist_id = m.watchlist_id
        WHERE w.watchlist_id = ?
        GROUP BY m.platform
        HAVING COUNT(m.item_id) >= ?
        ORDER BY titles DESC, m.platform ASC;
        """
        rows = self._conn.execute(sql, (watchlist_id, min_titles)).fetchall()
        return [dict(row) for row in rows]

#jo
def migrate_json_watchlist(repo: WatchlistRepository, json_path: Path = WATCHLIST_FILE) -> int:
    """Jednorazowa migracja: tylko gdy baza jest pusta. Plik JSON zmienia nazwę na .json.bak."""
    if repo.count_watchlists() > 0 or not json_path.exists():
        return 0
    try:
        watchlist = read_watchlist_file(json_path)
    except READ_ERRORS:
        print(f"[OSTRZEŻENIE] Nie udało się wczytać {json_path.name}, migracja pominięta.")
        return 0
    repo.save_watchlist(watchlist)
    json_path.replace(json_path.with_name(json_path.name + ".bak"))
    return len(watchlist)

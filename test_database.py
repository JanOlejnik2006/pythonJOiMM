#mm (edit:jo)
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

#mm
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from database import WatchlistRepository, get_connection, migrate_json_watchlist
from models import Movie, Series, Watchlist

#mm
def make_repo() -> WatchlistRepository:
    """Każdy test dostaje świeżą bazę w pamięci RAM, więc nie rusza prawdziwych danych."""
    return WatchlistRepository(get_connection(":memory:"))

#mm
def make_watchlist() -> Watchlist:
    return Watchlist("Do obejrzenia", [
        Movie(1, "Incepcja", "Sci-Fi", "Netflix", 148, "2010-07-16", True, 9.0, "Christopher Nolan"),
        Series(2, "Breaking Bad", "Dramat", "Netflix", 5, 12, 47, "2008-01-20"),
    ])

#mm
def test_1_schemat_z_kluczem_obcym():
    repo = make_repo()
    tables = {row["name"] for row in repo._conn.execute("SELECT name FROM sqlite_master WHERE type = 'table';")}
    assert {"watchlists", "media_items"} <= tables
    fk = repo._conn.execute("PRAGMA foreign_key_list(media_items);").fetchone()
    assert fk["table"] == "watchlists"
    assert fk["on_delete"] == "CASCADE"
    assert repo._conn.execute("PRAGMA foreign_keys;").fetchone()[0] == 1

#mm
def test_2_klucz_obcy_blokuje_sierote():
    repo = make_repo()
    try:
        repo.add_item(999, Movie(1, "Incepcja", "Sci-Fi", "Netflix", 148))
        assert False, "Pozycja bez watchlisty powinna rzucić IntegrityError"
    except sqlite3.IntegrityError:
        pass
    assert repo._conn.execute("SELECT COUNT(*) FROM media_items;").fetchone()[0] == 0

#mm
def test_3_repozytorium_zapis_i_odczyt():
    repo = make_repo()
    watchlist = make_watchlist()
    watchlist_id = repo.save_watchlist(watchlist)
    loaded = repo.load_watchlist(watchlist_id)
    assert loaded == watchlist
    assert repo.count_items(watchlist_id) == 2
    assert type(loaded.items[1]) is Series
    assert loaded.items[0].rating == 9.0
    assert loaded.items[1].runtime_minutes() == 2820

#mm
def test_4_kaskadowe_usuwanie():
    repo = make_repo()
    watchlist_id = repo.save_watchlist(make_watchlist())
    repo.delete_watchlist(watchlist_id)
    assert repo.count_items(watchlist_id) == 0
    assert repo.count_watchlists() == 0

#mm
def test_5_migracja_z_json():
    repo = make_repo()
    data = {"name": "Do obejrzenia", "items": [
        {"type": "movie", "id": 1, "title": "Incepcja", "genre": "Sci-Fi", "platform": "Netflix",
         "release_date": "2010-07-16", "is_watched": False, "rating": None, "duration": "2:28"},
    ]}
    with tempfile.TemporaryDirectory() as folder:
        json_path = Path(folder) / "watchlist.json"
        json_path.write_text(json.dumps(data), encoding="utf-8")
        assert migrate_json_watchlist(repo, json_path) == 1
        assert not json_path.exists()
        assert (Path(folder) / "watchlist.json.bak").exists()
        assert migrate_json_watchlist(repo, json_path) == 0
    loaded = repo.load_watchlist(repo.first_watchlist_id())
    assert loaded.items[0].title == "Incepcja"
    assert loaded.items[0].runtime_minutes() == 148

#mm
def test_6_wiezy_check_i_duplikaty():
    repo = make_repo()
    watchlist_id = repo.save_watchlist(Watchlist())
    bad_rows = [
        (11.0, 0, 100),  # ocena spoza 1-10
        (None, 2, 100),  # is_watched tylko 0 albo 1
        (None, 0, 0),    # czas musi być większy od zera
    ]
    for rating, is_watched, duration in bad_rows:
        try:
            with repo._conn:
                repo._conn.execute(
                    "INSERT INTO media_items (watchlist_id, media_id, title, genre, platform, rating, is_watched, duration_min) "
                    "VALUES (?, 1, 'Test', 'Dramat', 'Netflix', ?, ?, ?);",
                    (watchlist_id, rating, is_watched, duration),
                )
            assert False, f"CHECK powinien odrzucić wiersz {rating, is_watched, duration}"
        except sqlite3.IntegrityError:
            pass
    movie = Movie(1, "Incepcja", "Sci-Fi", "Netflix", 148)
    repo.add_item(watchlist_id, movie)
    try:
        repo.add_item(watchlist_id, movie)
        assert False, "UNIQUE powinien zablokować ten sam film drugi raz"
    except sqlite3.IntegrityError:
        pass
    assert repo.count_items(watchlist_id) == 1

#jo
def test_7_odpornosc_na_sql_injection():
    repo = make_repo()
    repo.save_watchlist(make_watchlist())
    assert len(repo.search_items("Incep")) == 1
    assert repo.search_items("' OR '1'='1") == []
    assert repo.search_items("%' OR 1=1 --") == []
    try:
        repo.search_items("", sort_by="title; DROP TABLE media_items")
        assert False, "Kolumna spoza białej listy powinna rzucić ValueError"
    except ValueError:
        pass
    assert len(repo.search_items("")) == 2
    assert [m.title for m in repo.search_items("", min_rating=9.0)] == ["Incepcja"]
    assert [m.title for m in repo.search_items("", is_watched=False)] == ["Breaking Bad"]

#jo
def test_8_rollback_przy_przenoszeniu():
    repo = make_repo()
    movie = Movie(1, "Incepcja", "Sci-Fi", "Netflix", 148)
    first = repo.save_watchlist(Watchlist("Lista A", [movie]))
    second = repo.save_watchlist(Watchlist("Lista B", [movie]))
    try:
        repo.move_item(movie, first, second)
        assert False, "Ten sam film na liście B powinien rzucić IntegrityError"
    except sqlite3.IntegrityError:
        pass
    assert repo.count_items(first) == 1, "ROLLBACK powinien przywrócić film na liście A"
    assert repo.count_items(second) == 1
    third = repo.save_watchlist(Watchlist("Lista C"))
    repo.move_item(movie, first, third)
    assert repo.count_items(first) == 0
    assert repo.count_items(third) == 1

#mm
TESTS = [
    test_1_schemat_z_kluczem_obcym,
    test_2_klucz_obcy_blokuje_sierote,
    test_3_repozytorium_zapis_i_odczyt,
    test_4_kaskadowe_usuwanie,
    test_5_migracja_z_json,
    test_6_wiezy_check_i_duplikaty,
    test_7_odpornosc_na_sql_injection,
    test_8_rollback_przy_przenoszeniu,
]

#mm
def main():
    failed = 0
    for test in TESTS:
        try:
            test()
            print(f"[OK]   {test.__name__}")
        except AssertionError as error:
            failed += 1
            print(f"[BŁĄD] {test.__name__}: {error}")
    print(f"\nWynik: {len(TESTS) - failed}/{len(TESTS)} testów zaliczonych.")
    if failed:
        raise SystemExit(1)

#mm
if __name__ == "__main__":
    main()

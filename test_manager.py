#mm
import sys
from pathlib import Path

#mm
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from manager import MediaCatalogManager
from models import MediaTitle, Movie, Series, media_from_dict

#mm
def make_catalog() -> MediaCatalogManager:
    return MediaCatalogManager([
        Movie(1, "Incepcja", "Sci-Fi", "Netflix", 148, "2010-07-16", True, 9.0, "Christopher Nolan"),
        Movie(2, "Gladiator", "Historyczny", "Max", 155, "2000-05-05"),
        Series(3, "Breaking Bad", "Dramat", "Netflix", 5, 12, 47, "2008-01-20", True, 9.5),
    ])

#mm
def test_1_klasa_bazowa_jest_abstrakcyjna():
    try:
        MediaTitle(1, "Coś", "Dramat", "Netflix")
        assert False, "Nie powinno dać się utworzyć obiektu klasy abstrakcyjnej"
    except TypeError:
        pass

#mm
def test_2_polimorfizm_czasu_i_wagi():
    movie = Movie(1, "Incepcja", "Sci-Fi", "Netflix", 120)
    series = Series(2, "Serial", "Dramat", "Max", 2, 10, 30)
    assert movie.runtime_minutes() == 120
    assert series.runtime_minutes() == 600
    assert movie.calculate_playback_weight() == 2.0
    assert series.calculate_playback_weight() == 11.67
    assert [media.kind_label() for media in (movie, series)] == ["Film", "Serial"]

#mm
def test_3_menedzer_sumy_i_raport():
    catalog = make_catalog()
    assert len(catalog) == 3
    assert catalog.total_runtime_minutes() == 148 + 155 + 2820
    assert catalog.total_runtime_hours() == 52.05
    assert catalog.count_by_kind() == {"Film": 2, "Serial": 1}
    report = {row["platforma"]: row for row in catalog.platform_report()}
    assert report["Netflix"]["pozycji"] == 2
    assert report["Netflix"]["srednia_ocena"] == 9.25
    assert report["Max"]["srednia_ocena"] is None
    assert catalog.next_id() == 4

#mm
def test_4_dyskryminator_typu_round_trip():
    catalog = make_catalog()
    rows = catalog.as_dicts()
    assert [row["type"] for row in rows] == ["movie", "movie", "series"]
    restored = MediaCatalogManager.from_dicts(rows)
    assert [media.kind_label() for media in restored.items] == ["Film", "Film", "Serial"]
    assert restored.items == catalog.items
    assert restored.total_runtime_minutes() == catalog.total_runtime_minutes()

#mm
def test_5_stare_i_bledne_dane():
    old = media_from_dict({"id": 7, "title": "Stary wpis", "duration": 100})
    assert old.kind_label() == "Film" and old.runtime_minutes() == 100
    try:
        media_from_dict({"id": 8, "title": "Gra", "type": "game"})
        assert False, "Nieznany typ powinien rzucić ValueError"
    except ValueError:
        pass
    try:
        Series(9, "Pusty serial", "Dramat", "Netflix", 0, 10, 40)
        assert False, "Zero sezonów powinno rzucić ValueError"
    except ValueError:
        pass

#mm
def test_6_menedzer_pilnuje_kolekcji():
    catalog = make_catalog()
    try:
        catalog.add(Movie(1, "Duplikat", "Sci-Fi", "Netflix", 100))
        assert False, "Zduplikowane ID powinno rzucić ValueError"
    except ValueError:
        pass
    try:
        catalog.add({"id": 10, "title": "Słownik"})
        assert False, "Dodanie słownika powinno rzucić TypeError"
    except TypeError:
        pass
    empty = MediaCatalogManager()
    assert empty.total_runtime_hours() == 0.0
    assert empty.platform_report() == []
    assert empty.next_id() == 1

#mm
def test_7_repr_i_str_w_podklasach():
    movie = Movie(1, "Incepcja", "Sci-Fi", "Netflix", 148, "2010-07-16", True, 9.0, "Christopher Nolan")
    series = Series(2, "Breaking Bad", "Dramat", "Netflix", 5, 12, 47, "2008-01-20", True, 9.5)
    for media in (movie, series):
        assert repr(eval(repr(media))) == repr(media)
    assert repr(movie).startswith("Movie(")
    assert repr(series).startswith("Series(")
    assert str(movie).endswith("| reż. Christopher Nolan")
    assert "5 sez. x 12 odc." in str(series)
    assert str(series).endswith("47 dni po 60 min")

#mm
TESTS = [
    test_1_klasa_bazowa_jest_abstrakcyjna,
    test_2_polimorfizm_czasu_i_wagi,
    test_3_menedzer_sumy_i_raport,
    test_4_dyskryminator_typu_round_trip,
    test_5_stare_i_bledne_dane,
    test_6_menedzer_pilnuje_kolekcji,
    test_7_repr_i_str_w_podklasach,
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

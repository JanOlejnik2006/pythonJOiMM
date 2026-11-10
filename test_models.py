#jo (edit:mm)
from src.models import MediaTitle, Movie, Series, Watchlist

#jo
def make_movies() -> list:
    return [
        Movie(1, "Incepcja", "Sci-Fi", "Netflix", 148, "2010-07-16", True, 9.0),
        Movie(2, "Gladiator", "Historyczny", "Max", 155, "2000-05-05", True, 8.0),
        Movie(3, "Shrek", "Animacja", "Netflix", 90, "2001-05-18"),
    ]

#jo
def test_1_poprawne_tworzenie():
    incepcja, gladiator, shrek = make_movies()
    assert incepcja.title_id == 1 and incepcja.year == 2010 and incepcja.rating == 9.0
    assert shrek.is_watched is False and shrek.rating is None
    watchlist = Watchlist("Na weekend", [incepcja, gladiator, shrek])
    assert len(watchlist) == 3
    assert watchlist.total_minutes() == 393
    assert watchlist.total_runtime_hours() == 6.55
    assert watchlist.average_rating() == 8.5

#jo
def test_2_odrzucenie_blednych_danych():
    shrek = make_movies()[2]
    try:
        shrek.rating = 8.0
        assert False, "Ocena nieobejrzanego filmu powinna rzucić ValueError"
    except ValueError:
        pass
    shrek.mark_watched(7.9)
    for bad_rating in (0.5, 10.5):
        try:
            shrek.rating = bad_rating
            assert False, f"Ocena {bad_rating} powinna rzucić ValueError"
        except ValueError:
            pass
    try:
        Movie(4, "Zły czas", "Dramat", "Max", -10)
        assert False, "Ujemny czas trwania powinien rzucić ValueError"
    except ValueError:
        pass
    try:
        Movie(5, "Zła data", "Dramat", "Max", 100, "16.07.2010")
        assert False, "Zły format daty powinien rzucić ValueError"
    except ValueError:
        pass

#jo
def test_3_sortowanie_lt():
    incepcja, gladiator, shrek = make_movies()
    movies = [shrek, gladiator, incepcja]
    movies.sort()
    assert [movie.title for movie in movies] == ["Incepcja", "Gladiator", "Shrek"]
    assert incepcja < gladiator
    assert gladiator < shrek

#jo
def test_4_round_trip():
    original = Watchlist("Na weekend", make_movies())
    restored = Watchlist.from_dict(original.to_dict())
    assert original == restored
    assert restored.items[0].rating == 9.0
    assert restored.items[2].is_watched is False

#jo
def test_5_duplikaty_i_typ():
    incepcja = make_movies()[0]
    watchlist = Watchlist()
    assert watchlist.add(incepcja) is True
    assert watchlist.add(Movie(1, "Ten sam film", "Sci-Fi", "Netflix", 148)) is False
    assert len(watchlist) == 1
    try:
        watchlist.add({"id": 2, "title": "Słownik"})
        assert False, "Dodanie słownika powinno rzucić TypeError"
    except TypeError:
        pass

#jo
def test_6_niezmienne_id_i_slots():
    incepcja = make_movies()[0]
    try:
        incepcja.title_id = 99
        assert False, "Zmiana ID powinna rzucić AttributeError"
    except AttributeError:
        pass
    try:
        incepcja.nowe_pole = 1
        assert False, "__slots__ powinno zablokować nowe pole"
    except AttributeError:
        pass

#jo
def test_7_dni_do_konca_serialu():
    serial = Series(1, "Breaking Bad", "Dramat", "Netflix", 5, 12, 47)
    assert serial.days_to_finish() == 47
    assert serial.days_to_finish(120) == 24
    assert Series(2, "Krótki", "Dramat", "Max", 1, 1, 30).days_to_finish() == 1
    assert not hasattr(Movie(3, "Incepcja", "Sci-Fi", "Netflix", 148), "days_to_finish")
    try:
        serial.days_to_finish(0)
        assert False, "Zero minut dziennie powinno rzucić ValueError"
    except ValueError:
        pass

#jo
TESTS = [
    test_1_poprawne_tworzenie,
    test_2_odrzucenie_blednych_danych,
    test_3_sortowanie_lt,
    test_4_round_trip,
    test_5_duplikaty_i_typ,
    test_6_niezmienne_id_i_slots,
    test_7_dni_do_konca_serialu,
]

#jo
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

#jo
if __name__ == "__main__":
    main()

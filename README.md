# CineStream

Menedżer kolekcji filmowej, recenzji i premier platform VOD.

Autorzy: Mateusz Mazur, Jan Olejnik

Uruchomienie: `python src/main.py`

Testy: `python test_models.py` i `python test_manager.py`


## Historia wersji

### 3.0.2 (2026-11-10)
- w watchliście opcja „Ile dni do końca serialu”: podajesz minuty dziennie, wynik zaokrąglony w górę
- czas w raporcie platform w godzinach i minutach zamiast ułamków godzin
- metoda days_to_finish() tylko dla seriali: ile dni do końca przy godzinie dziennie, widoczna w tabeli obok „HIT”
- autotest test_7_dni_do_konca_serialu
- podgląd pozycji w „Wyświetl kolekcję”: opis (__str__) i podgląd techniczny (__repr__)
- własny __str__ w Movie i Series przez super() (reżyser dla filmu, sezony, odcinki i dni do końca dla serialu)
- autotest test_7_repr_i_str_w_podklasach

### 3.0.1 (2026-11-10)
- klasa bazowa MediaTitle (ABC) i podklasy Movie oraz Series (dziedziczenie i polimorfizm)
- dodawanie filmu albo serialu (reżyser dla filmu, sezony i odcinki dla serialu)
- menedżer kolekcji MediaCatalogManager (łączny czas seansu, waga odtwarzania, raport platform)
- raport platform w menu i kolumna „Typ” w tabeli
- dyskryminator typu ("type") w zapisie JSON i fabryka media_from_dict
- autotesty menedżera w test_manager.py

### 3.0.0 (2026-11-03)
- klasy MediaTitle i Watchlist (programowanie obiektowe)
- watchlista zapisywana w pliku JSON
- oznaczanie filmu jako obejrzany i ocena tylko dla obejrzanych
- autotesty modeli w test_models.py
- tryb offline
- zapis atomowy i backupy
- usprawniona wyszukiwarka

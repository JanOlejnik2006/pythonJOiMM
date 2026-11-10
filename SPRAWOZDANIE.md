# Sprawozdanie z Zadania Laboratoryjnego nr 1
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Projekt:** CineStream  
**Zespół (Autorzy):**  
1. Mateusz Mazur (nr albumu: 164846) – login Git: `Mateusz863`
2. Jan Olejnik (nr albumu: [164857]) – login Git: `JanOlejnik2006`  
**Data oddania:** [13.10.2026]  

---

## 1. Cel i Zakres Inżynierski Zadania
Zrobiliśmy program w konsoli do zarządzania kolekcją filmów. Można w nim wyświetlić filmy, dodać nowy film, wyszukać film po tytule, filtrować po gatunku lub platformie i sortować. Po wpisaniu błędnych danych program pyta jeszcze raz. Użyliśmy pętli `while`, `match-case`, `try-except`, listy słowników i f-stringów.

W drugiej części dodaliśmy watchlistę („Do obejrzenia”) z łącznym czasem seansu. Główna kolekcja filmów jest teraz w bazie MongoDB Atlas, a plik `data.py` trzyma lokalną watchlistę. Każdy film ma też czas trwania w minutach.

---

## 2. Struktura plików
* `src/db.py` – połączenie z bazą MongoDB Atlas. Adres bazy jest w pliku `.env`, którego nie wrzucamy do gita. `load_movies()` pobiera wszystkie filmy z bazy, a `save_movie()` dodaje nowy film.
* `src/data.py` – lokalna watchlista (`WATCHLIST`). Każdy film to słownik z id, tytułem, gatunkiem, platformą, oceną i czasem trwania. Program sam zapisuje tu zmiany.
* `src/validators.py` – funkcje, które pobierają dane od użytkownika i sprawdzają, czy są poprawne (liczba całkowita, liczba z kropką lub przecinkiem, niepusty tekst).
* `src/services.py` – funkcje do pracy na filmach: tabela, która dopasowuje szerokość kolumn do danych, dodawanie filmu, filtrowanie, sortowanie, wyszukiwanie po tytule, watchlista (dodaj, usuń, łączny czas) i zapis watchlisty do `data.py`.
* `src/main.py` – menu w konsoli, menu watchlisty i pętla główna. Zapamiętuje ustawiony filtr i sortowanie, które działają przy każdym wyświetlaniu, dopóki ich nie zmienimy.

---

## 3. Kluczowy fragment kodu
* funkcja `get_float_input()` działa podobnie do `get_int_input()`, tylko pozwala wpisać liczbę z dokładnością do 0.1. Zrobiliśmy ją do oceniania filmów. Można wpisać kropkę albo przecinek (`7.5` i `7,5` znaczą to samo).
```python
def get_float_input(prompt: str, min_val: float = None, max_val: float = None) -> float:
    while True:
        raw = input(prompt).strip().replace(",", ".")
        if not raw:
            print("Błąd: Pusta wartość.")
            continue
        try:
            value = float(raw)
        except ValueError:
            print(f"Błąd: '{raw}' to nie liczba.")
            continue
        if not math.isfinite(value):
            print("Błąd: Niepoprawna liczba.")
            continue
        if round(value, 1) != value:
            print("Błąd: Maksymalnie jedna cyfra po kropce, np. 7.5")
            continue
        if min_val is not None and value < min_val:
            print(f"Błąd: Wartość < {min_val}")
            continue
        if max_val is not None and value > max_val:
            print(f"Błąd: Wartość > {max_val}")
            continue
        return value
```

**Uzasadnienie wyboru:**  
Ta funkcja pyta o liczbę tak długo, aż użytkownik poda poprawną. Przecinek zamieniamy na kropkę, a gdy ktoś wpisze litery, `float()` rzuca `ValueError`, który łapiemy w `try-except`. Gdy liczba jest spoza zakresu albo ma więcej niż jedną cyfrę po kropce, użytkownik dostaje komunikat i pytanie wraca (`continue`), więc program się nie zatrzymuje.

---

## 4. Testy

### Scenariusz A: poprawne dane
* **Co zrobiliśmy:** opcja 6, dodanie filmu `Avatar`, `Sci-Fi`, `Disney+`, ocena `7,8` (z przecinkiem), czas `162`. Potem opcja 2 (watchlista): dodanie Avatara i Incepcji, wyświetlenie watchlisty.
* **Wynik:**
```text
========================================
   CINESTREAM - KOLEKCJA FILMOWA   
========================================
Filtr: brak | Sortowanie: ID rosnąco
1. Szukaj po tytule
2. Watchlista
3. Wyświetl kolekcję
4. Sortuj
5. Filtruj
6. Dodaj film
7. Wyjście z programu
----------------------------------------
Wybierz opcję [1-7]: 6
Tytuł: Avatar
Gatunek: Sci-Fi
Platforma VOD: Disney+
Ocena [1-10, np. 7.5]: 7,8
Czas trwania [min]: 162
Dodano film o ID 5.
...
Wybierz opcję [1-6]: 2
1. Incepcja (148 min)
2. Gladiator (155 min)
3. Parasite (132 min)
4. Hobbit (169 min)
5. Avatar (162 min)
Wybierz film [1-5]: 5
Dodano film Avatar do watchlisty.
...
Wybierz opcję [1-6]: 1
ID   Tytuł    Gatunek Platforma    Czas Ocena
---------------------------------------------
1    Incepcja Sci-Fi  Netflix   148 min   9.0  HIT
5    Avatar   Sci-Fi  Disney+   162 min   7.8
Łączny czas seansu: 5 h 10 min
```
Avatar zapisał się w bazie MongoDB, a watchlista w `data.py`, więc po ponownym uruchomieniu programu oba nadal są.

### Scenariusz B: błędne dane
* **Co wpisaliśmy:** w menu `abc`; w tytule same spacje; w ocenie `4.42`, `abc`, `11`; w czasie trwania `0`; w wyszukiwarce `xyz`; przy wyborze filmu do watchlisty `9`.
* **Wynik:**
```text
Wybierz opcję [1-7]: abc
Błąd: Nieznana opcja. Wybierz wartość od 1 do 7.
...
Wybierz opcję [1-7]: 6
Tytuł: 
Tekst nie może być pusty.
Tytuł: Test
Gatunek: Dramat
Platforma VOD: Max
Ocena [1-10, np. 7.5]: 4.42
Błąd: Maksymalnie jedna cyfra po kropce, np. 7.5
Ocena [1-10, np. 7.5]: abc
Błąd: 'abc' to nie liczba.
Ocena [1-10, np. 7.5]: 11
Błąd: Wartość > 10
Ocena [1-10, np. 7.5]: 7.5
Czas trwania [min]: 0
Wartośc poza zakresem.
Czas trwania [min]: 90
Dodano film o ID 5.
...
Wybierz opcję [1-7]: 1
Szukana fraza w tytule: xyz
Brak filmów z frazą 'xyz' w tytule.
...
Wybierz opcję [1-6]: 2
1. Incepcja (148 min)
2. Gladiator (155 min)
3. Parasite (132 min)
4. Hobbit (169 min)
5. Test (90 min)
Wybierz film [1-5]: 9
Wartośc poza zakresem.
Wybierz film [1-5]: 1
Dodano film Incepcja do watchlisty.
```
Program za każdym razem pokazał błąd i zapytał jeszcze raz, albo wrócił do menu.

---

## 5. Podział pracy
* **Mateusz Mazur:**
  * Moduły: `src/main.py`, `README.md`, `SPRAWOZDANIE.md`
  * Co zrobił: menu, wybór opcji w menu, komunikaty dla użytkownika, sortowanie, drobne poprawki, oznaczenie HIT dla najlepszych filmów, czas trwania filmu, skrypt wysyłający filmy do MongoDB, przerobienie `data.py` na watchlistę, menu watchlisty z wyborem filmu z listy, filtrowanie i sortowanie w watchliście, tabela dopasowująca szerokość kolumn, wyszukiwarka po tytule, nowa kolejność menu
  * Liczba commitów: 17
* **Jan Olejnik:**
  * Moduły: `src/validators.py`, `src/data.py`, `src/services.py`, `src/db.py`
  * Co zrobił: walidatory, dane startowe, funkcje na filmach, filtrowanie po gatunku i platformie, zapis do pliku, oceny z kropką i przecinkiem, logika sortowania, połączenie z MongoDB, przeniesienie kolekcji do bazy (lista pobierana z bazy przy każdym wyświetleniu), logika watchlisty i łącznego czasu seansu, zapamiętywanie filtra i sortowania
  * Liczba commitów: 21

---

## Źródła wiedzy
* W3Schools – Python Tutorial: https://www.w3schools.com/python/ (m.in. pętle `while`, `try-except`, listy i słowniki, f-stringi, `match-case`)
* Materiały z wykładu (slajdy do Laboratorium 01.1)
* Dokumentacja PyMongo – Tutorial: https://pymongo.readthedocs.io/en/stable/tutorial.html (łączenie z bazą, `find`, `insert_one`, `insert_many`)
* Materiały z wykładu (slajdy do Laboratorium 01.2 – filtrowanie z `casefold()`, wyszukiwanie po ID, wzorzec aktywnego rachunku BrewMaster)

---
---

# Zadanie 2 – Persystencja danych (pliki CSV)

## 1. Cel
Watchlista nie jest już zapisywana w pliku `data.py`, tylko w pliku `data/watchlist.csv`. Cały kod do obsługi plików przenieśliśmy do nowego modułu `storage.py`, więc `main.py` nie otwiera żadnych plików sam. Główna kolekcja filmów zostaje w bazie MongoDB Atlas (zamiast pliku JSON z instrukcji). Program nie wywala się, gdy pliku nie ma, gdy jest uszkodzony albo gdy nie ma połączenia z bazą.

## 2. Zmiany w strukturze plików
* `src/storage.py` – nowy moduł: `load_watchlist()` czyta `data/watchlist.csv` przez `csv.DictReader`, a `save_watchlist()` zapisuje przez `csv.DictWriter`. Ścieżka jest zrobiona przez `pathlib`, a folder `data/` tworzy się sam.
* `data/watchlist.csv` – plik z watchlistą (id, tytuł, gatunek, platforma, ocena, czas). Jest w `.gitignore`, bo zmienia się przy każdym użyciu programu.
* `src/data.py` – trzyma teraz tylko `VIEW`, czyli aktualny filtr i sortowanie.
* `src/db.py` – połączenie z MongoDB czeka maksymalnie 5 sekund, a `main.py` pokazuje komunikat, gdy bazy nie ma.
* `src/services.py` – doszła funkcja `average_rating()` (średnia ocena w watchliście), a stary zapis do `data.py` usunęliśmy.

## 3. Kluczowy fragment kodu
```python
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
```

**Uzasadnienie wyboru:**  
Gdy pliku nie ma (pierwsze uruchomienie), łapiemy `FileNotFoundError`, tworzymy pusty plik z nagłówkiem i zaczynamy z pustą watchlistą. `DictReader` zwraca same napisy, więc id, ocenę i czas zamieniamy z powrotem na liczby, a gdy plik jest uszkodzony (zły format, brak kolumn), łapiemy `ValueError`/`KeyError` i program działa dalej.

## 4. Testy

### Scenariusz A: pierwsze uruchomienie i zapis
* **Co zrobiliśmy:** usunęliśmy folder `data/`, uruchomiliśmy program, w watchliście dodaliśmy Incepcję i film z polskimi znakami. Potem zamknęliśmy i włączyliśmy program jeszcze raz.
* **Wynik:** program sam utworzył `data/watchlist.csv`, a po każdym dodaniu plik od razu się zmieniał:
```text
id,title,genre,platform,rating,duration
1,Incepcja,Sci-Fi,Netflix,9,148
3,Łódź Kaliska ąę,Komedia,CDA,7.5,95
```
Po ponownym uruchomieniu watchlista się wczytała:
```text
1    Incepcja        Sci-Fi  Netflix   148 min   9.0  HIT
3    Łódź Kaliska ąę Komedia CDA        95 min   7.5
Łączny czas seansu: 4 h 3 min
Średnia ocena: 8.2
```

### Scenariusz B: uszkodzony plik i brak bazy
* **Co zrobiliśmy:** w `watchlist.csv` wpisaliśmy `abc` zamiast oceny, potem same śmieci bez nagłówka, a na koniec pusty plik. Osobno uruchomiliśmy program ze złym adresem bazy.
* **Wynik:**
```text
Błąd: Plik watchlist.csv jest uszkodzony, watchlista zaczyna się od nowa.
...
Błąd: Brak połączenia z bazą MongoDB. Sprawdź internet i plik .env.
```
Przy pustym pliku program po prostu pokazał pustą watchlistę. W żadnym przypadku nie było `Traceback` ani `FileNotFoundError` w konsoli.

## 4a. Odporność persystencji (Laboratorium 2.2)

**Co doszło:**
* **Zapis atomowy** – `save_watchlist()` zapisuje najpierw do pliku tymczasowego (`tempfile`), wymusza zapis na dysk (`os.fsync`) i dopiero wtedy podmienia plik przez `os.replace`. Przerwanie programu w trakcie zapisu nie psuje starej watchlisty.
* **Kopie zapasowe z rotacją** – przed każdym zapisem `backup_watchlist()` kopiuje plik do `data/backups/watchlist_RRRRMMDD_GGMMSS.bak` (`shutil.copy2`) i usuwa najstarsze, tak żeby zostały 3.
* **Kwarantanna i auto-naprawa** – gdy `watchlist.csv` jest pusty albo uszkodzony, `repair_watchlist()` przenosi go do `data/corrupted_<data>.csv`, przywraca najnowszą dobrą kopię `.bak`, a gdy takiej nie ma, zaczyna od pustej watchlisty i pokazuje ostrzeżenie.
* **Migracja danych** – `load_movies()` uzupełnia brakujące pola w starszych filmach z bazy (np. brak platformy → „brak”, brak czasu → 0 min).
* **Czas w pliku watchlisty** – w `watchlist.csv` czas trwania zapisujemy jako godzina:minuta (np. `2:28`), a przy wczytywaniu zamieniamy go z powrotem na minuty. W programie czas dalej jest w minutach, a stare pliki z czasem w minutach (`148`) też się wczytują.
* **Katalog filmów w MongoDB** – każdy zapis (`insert_one`) jest w bazie atomowy, więc tam nie trzeba plików tymczasowych.
* **Brak internetu** – gdy nie ma połączenia z bazą (przy starcie albo w trakcie działania), program pokazuje komunikat o braku internetu i informację, że tryb offline będzie dostępny już niedługo, zamiast się wywalać. Połączenie z bazą (`connect=False`) nawiązuje się dopiero przy pierwszym zapytaniu, więc brak internetu nie wywala programu już przy imporcie.
* **Data premiery** – każdy film ma datę premiery (`RRRR-MM-DD`, sprawdzaną przez `get_date_input()`), widoczną w tabeli i dostępną w sortowaniu. Starsze filmy i stara watchlista bez tego pola dostają `-` (migracja przy wczytywaniu).
* **Tryb offline (kopia JSON)** – dodano zapis filmów z bazy do `data/movies_cache.json` i sprawdzanie połączenia, żeby program działał w trybie offline.
* **Kolejkowanie dodawania offline** – dodawanie filmów w trybie offline zapisuje je lokalnie do `data/pending_movies.json`, a po połączeniu z bazą wysyła je na serwer. Jeśli w tym czasie ktoś inny dodał film z tym samym ID, film z kolejki dostaje nowe, wolne ID, więc w bazie nie ma duplikatów.

**Kluczowy fragment kodu:**
```python
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
```
Uszkodzonego pliku nie kasujemy, tylko odkładamy do kwarantanny, żeby można go było potem obejrzeć. Kopie sprawdzamy od najnowszej i bierzemy pierwszą, która się poprawnie wczytuje.

**Test awaryjny:**
* **Usunięcie pliku:** usunęliśmy folder `data/` → program wystartował z pustą watchlistą i sam utworzył `data/watchlist.csv`.
* **Rotacja kopii:** dodaliśmy 4 filmy w osobnych uruchomieniach → w `data/backups/` zostały 3 najnowsze kopie.
* **Uszkodzenie pliku:** w `watchlist.csv` wpisaliśmy `abc` zamiast id, a potem wyczyściliśmy plik do 0 bajtów:
```text
[OSTRZEŻENIE] Plik watchlist.csv jest uszkodzony, przeniesiono go do corrupted_20261027_185613.csv.
Przywrócono watchlistę z kopii watchlist_20261027_185611.bak.
1    Incepcja Sci-Fi  Netflix   148 min   9.0  HIT
Łączny czas seansu: 2 h 28 min
```
* **Uszkodzenie pliku i wszystkich kopii:**
```text
[OSTRZEŻENIE] Plik watchlist.csv jest uszkodzony, przeniesiono go do corrupted_20261027_185613.csv.
Brak dobrej kopii zapasowej, watchlista zaczyna się od nowa.
```
* **Przerwanie zapisu:** zasymulowaliśmy Ctrl+C w trakcie zapisu → stary `watchlist.csv` został cały, a niedokończony był tylko plik tymczasowy.
W żadnym teście program się nie wywalił i nie pokazał `Traceback`.

## 5. Podział pracy (Zadanie 2)
* **Mateusz Mazur:** podpięcie watchlisty pod `storage.py` w `main.py` i `services.py`, średnia ocena w watchliście, opcja „0. Anuluj” przy wyborze filmu do dodania lub usunięcia, podpowiedź „Czy chodziło o…?” przy literówce w wyszukiwarce, kopie zapasowe z rotacją, uzupełnianie brakujących pól filmów, komunikat o braku internetu, data premiery filmów, sprawozdanie do Zadania 2, status online/offline w menu, tryb offline (filmy z bazy albo z kopii JSON, blokada dodawania offline), sprawozdanie o trybie offline, ponowne łączenie online w menu, drobne poprawki – 16 commitów.
* **Jan Olejnik:** moduł `storage.py` (zapis i odczyt CSV, obsługa braku i uszkodzenia pliku), przeniesienie filtra i sortowania do `data.py`, komunikat przy braku połączenia z bazą, źródła w sprawozdaniu, lepsza wyszukiwarka (bez polskich znaków i wielkości liter, kilka słów w dowolnej kolejności, szukanie też po gatunku i platformie), zapis atomowy watchlisty, kwarantanna uszkodzonego pliku i odtwarzanie z kopii, czas w pliku watchlisty w formacie godzina:minuta, poprawka komunikatu przy braku internetu, sprawdzanie internetu pingiem, zapis atomowy kopii filmów do JSON z kopiami zapasowymi, odczyt kopii JSON z kwarantanną i odtworzeniem z .bak, priorytet wyników zaczynających się od szukanej frazy, data aktualizacji lokalnego zapisu w menu, usunięcie zbędnych źródeł, kolejkowanie dodawania filmów offline, poprawka zajętych ID przy wysyłaniu kolejki – 17 commitów.
* **Łącznie w repozytorium:** Jan Olejnik 44 commity, Mateusz Mazur 43 commity (razem z Zadaniem 3).

---
---

# Zadanie 3 – Programowanie obiektowe (OOP)

## 1. Cel
Zamiast samych słowników mamy teraz klasy w `src/models.py`. Film to obiekt `MediaTitle`, który sam pilnuje poprawności swoich danych, a watchlista to agregat `Watchlist`, który zarządza listą filmów. Program dalej korzysta z MongoDB, a watchlista jest zapisywana jako zagnieżdżony JSON.

## 2. Zmiany w strukturze plików
* `src/models.py` – nowy moduł z dwiema klasami:
  * `MediaTitle` (encja): ID, tytuł, gatunek, platforma, czas trwania, data premiery (z niej liczony jest `year`), `is_watched` i ocena. Pola są chronione przez `@property` z setterami, ID jest tylko do odczytu (bez settera), a `__slots__` blokuje dopisywanie nowych pól. Ma `__repr__`, `__str__`, `__eq__` (po ID), `__lt__` (sortowanie po ocenie malejąco) oraz `to_dict()` i `from_dict()`.
  * `Watchlist` (agregat): dodaje filmy bez duplikatów (`__eq__`), usuwa, oznacza jako obejrzane (`mark_watched`), liczy `total_runtime_hours()` i średnią ocen, ma `to_dict()`/`from_dict()` z zagnieżdżoną listą filmów.
* `test_models.py` – autotesty modeli, uruchamiane przez `python test_models.py`.
* `src/storage.py` – watchlista zapisuje się do `data/watchlist.json` w formacie `{"name": ..., "items": [...]}` (zapis atomowy, kopie `.bak`, kwarantanna jak wcześniej). Stary `watchlist.csv` przenosi się sam przy pierwszym uruchomieniu.
* `src/db.py` – filmy z bazy przechodzą przez `MediaTitle` (`normalize_movies`), a `update_movie()` zapisuje ocenę w bazie.
* `src/main.py` – przy dodawaniu filmu program pyta, czy jest obejrzany (ocena tylko dla obejrzanych). W watchliście doszła opcja „Oznacz jako obejrzany i oceń”.

## 3. Kluczowy fragment kodu
```python
@rating.setter
def rating(self, value: float | None) -> None:
    """Niezmiennik: ocenę można dać tylko obejrzanemu filmowi."""
    if value is None:
        self._rating = None
        return
    if not self._is_watched:
        raise ValueError("Nie można ocenić filmu, który nie jest obejrzany.")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("Ocena musi być liczbą.")
    if not 1.0 <= value <= 10.0:
        raise ValueError(f"Ocena musi być w zakresie 1.0-10.0 (podano: {value}).")
    self._rating = round(float(value), 1)
```

**Uzasadnienie wyboru:**  
To niezmiennik z zadania: oceny 1.0–10.0 nie da się przypisać filmowi, który nie jest obejrzany, bo setter od razu rzuca `ValueError`. Dzięki temu żadna część programu nie może doprowadzić filmu do złego stanu, a menu nie musi tego osobno sprawdzać.

## 4. Testy
* **Autotesty** (`python test_models.py`): poprawne tworzenie obiektów, odrzucenie błędnych danych (`ValueError`), sortowanie przez `__lt__`, round-trip `to_dict()`/`from_dict()` oraz dodatkowo duplikaty, niezmienne ID i `__slots__`:
```text
[OK]   test_1_poprawne_tworzenie
[OK]   test_2_odrzucenie_blednych_danych
[OK]   test_3_sortowanie_lt
[OK]   test_4_round_trip
[OK]   test_5_duplikaty_i_typ
[OK]   test_6_niezmienne_id_i_slots
[OK]   test_7_dni_do_konca_serialu

Wynik: 7/7 testów zaliczonych.
```
* **Dni do końca serialu:** metoda `days_to_finish()` jest tylko w klasie `Series` (film nie ma sezonów i odcinków). Liczy, ile dni zajmie obejrzenie całego serialu przy godzinie dziennie, i zaokrągla w górę. W tabeli pokazuje się na końcu wiersza serialu, podobnie jak „HIT”:
```text
2    Serial Breaking Bad Dramat  Netflix   2008-01-20 2820 min   9.5  HIT  47 dni po 60 min
3    Serial Czarnobyl    Dramat  Max       -          325 min     -  6 dni po 60 min
```
* **W programie:** film dodany jako nieobejrzany ma ocenę `-`, a po opcji „Oznacz jako obejrzany i oceń” na watchliście dostaje ocenę, która zapisuje się też w bazie (offline tylko na watchliście, z komunikatem):
```text
Film Incepcja oznaczono jako obejrzany z oceną 9.2.
Ocena zapisana też w bazie.
1    Incepcja Sci-Fi  Netflix   2010-07-16 148 min   9.2  HIT
```
* **Przeniesienie starej watchlisty:** `Przeniesiono watchlistę z watchlist.csv do watchlist.json.`

## 4b. Dziedziczenie, polimorfizm i menedżer (Laboratorium 3.2)

**Hierarchia klas:**
```text
                  MediaTitle (ABC)
   wspólne: title_id, title, genre, platform, release_date,
            is_watched, rating, year, mark_watched()
   abstrakcyjne: runtime_minutes(), calculate_playback_weight(), kind_label()
                         │
          ┌──────────────┴──────────────┐
        Movie                         Series
  duration_min, director      seasons, episodes_per_season,
  type = "movie"              minutes_per_episode, type = "series"

  Watchlist ──(1:N)──▶ MediaTitle      MediaCatalogManager ──(1:N)──▶ MediaTitle
```

**Co doszło:**
* `MediaTitle` jest teraz **klasą abstrakcyjną** (`ABC`). Nie da się utworzyć jej obiektu (`TypeError`), tylko obiekt podklasy. Podklasy wywołują `super().__init__()` dla wspólnych pól.
* **Polimorfizm:** `Movie` i `Series` mają własne `runtime_minutes()`, `calculate_playback_weight()` i `kind_label()`. Film liczy czas z jednego seansu, a serial z sezonów, odcinków i długości odcinka (waga dolicza 5 minut czołówki na każdy odcinek). Reszta programu wywołuje te metody bez sprawdzania, czy to film, czy serial.
* **Menedżer `MediaCatalogManager`** (`src/manager.py`): dodaje pozycje (pilnuje typu i duplikatów ID), liczy łączny czas seansu, wagę odtwarzania, liczbę filmów i seriali oraz robi raport platform. Menu wyświetla kolekcję, dodaje pozycje i pokazuje raport przez menedżera.
* **Dyskryminator typu:** `to_dict()` dopisuje pole `"type"` (`"movie"` albo `"series"`), a fabryka `media_from_dict()` wybiera klasę ze słownika `MEDIA_REGISTRY`. Stare wpisy bez typu są wczytywane jako filmy.
* W menu: „6. Dodaj film lub serial” (dla filmu pyta o reżysera, dla serialu o sezony i odcinki), „7. Raport platform” i kolumna „Typ” w tabeli.

**Kluczowy fragment – fabryka typów:**
```python
def media_from_dict(data: dict) -> MediaTitle:
    """Fabryka: wybiera klasę po polu "type" bez drabinki if/elif. Stare wpisy bez typu to filmy."""
    type_tag = data.get("type", "movie")
    target_cls = MEDIA_REGISTRY.get(type_tag)
    if target_cls is None:
        raise ValueError(f"Nieznany typ pozycji w danych: {type_tag!r}")
    return target_cls.from_dict(data)
```
Dzięki rejestrowi dodanie nowego rodzaju pozycji to dopisanie jednej klasy i jednej linijki w `MEDIA_REGISTRY`, bez zmieniania kodu, który wczytuje dane.

**Autotesty menedżera** (`python test_manager.py`):
```text
[OK]   test_1_klasa_bazowa_jest_abstrakcyjna
[OK]   test_2_polimorfizm_czasu_i_wagi
[OK]   test_3_menedzer_sumy_i_raport
[OK]   test_4_dyskryminator_typu_round_trip
[OK]   test_5_stare_i_bledne_dane
[OK]   test_6_menedzer_pilnuje_kolekcji
[OK]   test_7_repr_i_str_w_podklasach

Wynik: 7/7 testów zaliczonych.
```

**`__repr__` i `__str__` w podklasach:** każda podklasa ma własny `__repr__`, który zwraca „przepis” na odtworzenie obiektu – test sprawdza, że `eval(repr(obj))` daje taki sam obiekt. `__str__` w `Movie` i `Series` bierze opis z klasy bazowej przez `super().__str__()` i dopisuje swoje: film reżysera, serial sezony, odcinki i dni do końca. W opcji „Wyświetl kolekcję” po tabeli można podać ID i zobaczyć oba opisy:
```text
Podaj ID pozycji do podglądu (0 = pomiń): 1
[01] Film: Incepcja (2010) | Sci-Fi | 148 min | ocena: 9.0 | reż. Christopher Nolan
Podgląd techniczny (repr): Movie(title_id=1, title='Incepcja', genre='Sci-Fi', platform='Netflix', duration_min=148, release_date='2010-07-16', is_watched=True, rating=9.0, director='Christopher Nolan')
```

**Raport platform w programie:**
```text
Platforma          Pozycji Śr. ocena          Czas
Amazon Prime Video       1         -    2 h 35 min
Netflix                  2      9.25   49 h 28 min
Razem: 3 pozycji, 52 h 03 min
```

## 5. Podział pracy (Zadanie 3)
* **Mateusz Mazur:** klasa `MediaTitle` z walidacją i niezmiennikiem oceny, agregat `Watchlist`, zapis watchlisty jako zagnieżdżony JSON i przeniesienie starego CSV, oznaczanie filmu jako obejrzany i ocena w watchliście, sprawozdanie do Zadania 3, klasa bazowa `MediaTitle` (ABC) i podklasa `Movie`, menedżer `MediaCatalogManager`, autotesty `test_manager.py`, raport platform w menu, wywołanie `__repr__` w podglądzie pozycji i `__str__` nadpisany w każdej podklasie – 12 commitów.
* **Jan Olejnik:** `__repr__`, `__str__`, `__eq__`, `__lt__`, `to_dict()` i `from_dict()` w `MediaTitle`, autotesty `test_models.py`, filmy w kolekcji przez `MediaTitle`, pole „obejrzany” przy dodawaniu i obsługa filmów bez oceny, podklasa `Series` i fabryka z dyskryminatorem typu, menu przez menedżera i dodawanie filmu lub serialu, historia wersji w README, czas w raporcie platform w godzinach i minutach, metoda „dni do końca” tylko dla seriali – 9 commitów.

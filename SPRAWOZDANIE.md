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

## 5. Podział pracy (Zadanie 2)
* **Mateusz Mazur:** podpięcie watchlisty pod `storage.py` w `main.py` i `services.py`, średnia ocena w watchliście, opcja „0. Anuluj” przy wyborze filmu do dodania lub usunięcia, podpowiedź „Czy chodziło o…?” przy literówce w wyszukiwarce, sprawozdanie do Zadania 2 – 5 commitów.
* **Jan Olejnik:** moduł `storage.py` (zapis i odczyt CSV, obsługa braku i uszkodzenia pliku), przeniesienie filtra i sortowania do `data.py`, komunikat przy braku połączenia z bazą, źródła w sprawozdaniu, lepsza wyszukiwarka (bez polskich znaków i wielkości liter, kilka słów w dowolnej kolejności, szukanie też po gatunku i platformie) – 4 commity.
* **Łącznie w repozytorium:** Jan Olejnik 25 commitów, Mateusz Mazur 22 commity.


**Źródła (Zadanie 2):** slajdy do Laboratorium 2.1 (moduł `storage.py`, `csv.DictReader`/`DictWriter`, `pathlib`, obsługa `FileNotFoundError`), dokumentacja Pythona – moduł `csv`: https://docs.python.org/3/library/csv.html

**Kurs online:** Udemy – Python for Beginners: https://www.udemy.com/course/pythonforbeginnersintro/

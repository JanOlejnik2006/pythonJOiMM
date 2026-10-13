# Sprawozdanie z Zadania Laboratoryjnego nr 1
**Przedmiot:** Programowanie w języku Python (`IwIK-S1`)  
**Projekt:** CineStream  
**Zespół (Autorzy):**  
1. Mateusz Mazur (nr albumu: 164846) – login Git: `Mateusz863`
2. Jan Olejnik (nr albumu: [164857]) – login Git: `JanOlejnik2006`  
**Data oddania:** [13.10.2026]  

---

## 1. Cel zadania
Zrobiliśmy program w konsoli do zarządzania kolekcją filmów. Można w nim wyświetlić filmy, dodać nowy film i filtrować po gatunku. Program ma po wpisaniu błędnych danych zapytać jeszcze raz. Użyliśmy pętli `while`, `match-case`, `try-except`, listy słowników i f-stringów.

---

## 2. Struktura plików
* `src/data.py` – lista filmów (`MOVIES`). Każdy film to słownik z id, tytułem, gatunkiem, platformą i oceną. Nowe filmy zapisują się tu automatycznie.
* `src/validators.py` – funkcje, które pobierają dane od użytkownika i sprawdzają, czy są poprawne (liczba całkowita, liczba z kropką, niepusty tekst).
* `src/services.py` – funkcje do pracy na filmach: wyświetlanie tabeli, dodawanie filmu, filtrowanie po gatunku, zapis do `data.py`.
* `src/main.py` – menu w konsoli i pętla główna, która wywołuje resztę funkcji.

---

## 3. Kluczowy fragment kodu
* funkcja 'get_float_input()' to funkcja analogiczna do funkcji "get_int_input" z tym, ze pozwala ona wpisywac wartosci z dokladnoscia 0.1, zostala utworzona do systemu oceniania filmow 
```python
def get_float_input(prompt: str, min_val: float = None, max_val: float = None) -> float:
    while True:
        raw = input(prompt).strip()
        if "," in raw:
            print("Błąd: Użyj kropki zamiast przecinka, np. 7.5")
            continue
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
Ta funkcja pyta użytkownika o liczbę tak długo, aż poda poprawną. Gdy wpisze litery albo pustą linię, `int()` rzuca `ValueError`, który łapiemy w `try-except`. Gdy liczba jest spoza zakresu, też dostaje komunikat. W obu przypadkach pytanie wraca (`continue`), więc program się nie zatrzymuje. Użyliśmy jej w wyborze gatunku z listy, a podobnie działa walidator ocen z kropką.

---

## 4. Testy

### Scenariusz A: poprawne dane
* **Co zrobiliśmy:** opcja 2, dodanie filmu: `Matrix`, `Sci-Fi`, `Netflix`, ocena `7.5`. Potem opcja 1.
* **Wynik:**
```text
========================================
   CINESTREAM - KOLEKCJA FILMOWA   
========================================
1. Wyświetl kolekcję
2. Dodaj film
3. Filtruj po gatunku
4. Wyjście z programu
----------------------------------------
Wybierz opcję [1-4]: 2
Tytuł: Test 2
Gatunek: Inny
Platforma VOD: YouTube
Ocena [1-10, np. 7.5]: 5.6
Dodano film o ID 6.
```
Po zamknięciu i ponownym uruchomieniu programu film nadal jest na liście, bo zapisał się w `data.py`.

### Scenariusz B: błędne dane
* **Co wpisaliśmy:** w menu `abc`; w ocenie `7,5`, `4.42`, `abc`, `11` i pustą linię; w tytule same spacje.
* **Wynik:**
```text
========================================
   CINESTREAM - KOLEKCJA FILMOWA   
========================================
1. Wyświetl kolekcję
2. Dodaj film
3. Filtruj po gatunku
4. Wyjście z programu
----------------------------------------
Wybierz opcję [1-4]: abc
Błąd: Nieznana opcja. Wybierz wartość od 1 do 4.

========================================
   CINESTREAM - KOLEKCJA FILMOWA   
========================================
1. Wyświetl kolekcję
2. Dodaj film
3. Filtruj po gatunku
4. Wyjście z programu
----------------------------------------
Wybierz opcję [1-4]: 2
Tytuł: 
Tekst nie może być pusty.
Tytuł: test3
Gatunek: testowy
Platforma VOD: testowa
Ocena [1-10, np. 7.5]: 7,5
Błąd: Użyj kropki zamiast przecinka, np. 7.5
Ocena [1-10, np. 7.5]: 4.42
Błąd: Maksymalnie jedna cyfra po kropce, np. 7.5
Ocena [1-10, np. 7.5]: abc
Błąd: 'abc' to nie liczba.
Ocena [1-10, np. 7.5]: 11
Błąd: Wartość > 10
Ocena [1-10, np. 7.5]: 7.5
Dodano film o ID 8.

```
Program za każdym razem pokazał błąd i zapytał jeszcze raz, albo wrócił do menu.

---

## 5. Podział pracy
* **Mateusz Mazur:**
  * Moduły: `src/main.py`, `README.md`, `SPRAWOZDANIE.md`
  * Co zrobił: menu, wybór opcji w menu, komunikaty dla użytkownika
  * Liczba commitów: 6
* **Jan Olejnik:**
  * Moduły: `src/validators.py`, `src/data.py`, `src/services.py`
  * Co zrobił: walidatory, dane startowe, funkcje na filmach, filtrowanie, zapis do pliku, oceny z kropką
  * Liczba commitów: 9

---

## Źródła wiedzy
* W3Schools – Python Tutorial: https://www.w3schools.com/python/ (m.in. pętle `while`, `try-except`, listy i słowniki, f-stringi, `match-case`)
* Materiały z wykładu (slajdy do Laboratorium 01.1)
s
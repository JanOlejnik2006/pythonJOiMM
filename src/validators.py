import math


def get_int_input(prompt, min_val, max_val):
    while True:
        raw = input(prompt).strip()
        try:
            value = int(raw)
        except ValueError:
            print("To nie jest liczba.")
            continue

        if min_val <= value <= max_val:
            return value

        print(f"Liczba musi być z zakresu od {min_val} do {max_val}.")


def get_non_empty_string(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Tekst nie może być pusty.")



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
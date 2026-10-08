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
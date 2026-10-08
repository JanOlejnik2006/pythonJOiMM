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
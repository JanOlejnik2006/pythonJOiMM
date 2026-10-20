#jo (edit:mm)
from data import MOVIES
from services import add_item, display_items, filter_by_field, get_field_values, save_items, sort_by_field
from validators import get_float_input, get_int_input, get_non_empty_string

#jo (edit:mm)
FILTER_FIELDS = {
    1: ("genre", "gatunek"),
    2: ("platform", "platforma"),
}

#jo (edit:mm)
SORT_FIELDS = {
    1: ("id", "ID"),
    2: ("title", "tytuł"),
    3: ("genre", "gatunek"),
    4: ("platform", "platforma"),
    5: ("rating", "ocena"),
    6: ("duration", "czas trwania"),
}

#jo(edit:mm)
SORT_ORDERS = {
    1: ("rosnąco", False),
    2: ("malejąco", True),
}

#mm
def print_menu():
    print("\n" + "=" * 40)
    print("   CINESTREAM - KOLEKCJA FILMOWA   ")
    print("=" * 40)
    print("1. Wyświetl kolekcję")
    print("2. Dodaj film")
    print("3. Filtruj (gatunek / platforma)")
    print("4. Sortuj (ID / tytuł / gatunek / platforma / ocena / czas)")
    print("5. Wyjście z programu")
    print("-" * 40)

#mm
def show_movies():
    display_items(MOVIES)

#mm (edit:jo)
def read_movie_data() -> dict:
    return {
        "title": get_non_empty_string("Tytuł: "),
        "genre": get_non_empty_string("Gatunek: "),
        "platform": get_non_empty_string("Platforma VOD: "),
        "rating": get_float_input("Ocena [1-10, np. 7.5]: ", 1, 10),
        "duration": get_int_input("Czas trwania [min]: ", 1, 600),
    }

#mm (edit:jo)
def add_movie():
    added = add_item(MOVIES, read_movie_data())
    save_items(MOVIES)
    print(f"Dodano film o ID {added['id']}.")
#jo (edit:mm)
def choose_filter_field() -> tuple[str, str]:
    print("Filtruj po:")
    for number, (_, label) in FILTER_FIELDS.items():
        print(f"{number}. {label.capitalize()}")
    choice = get_int_input(f"Wybierz kryterium [1-{len(FILTER_FIELDS)}]: ", 1, len(FILTER_FIELDS))
    return FILTER_FIELDS[choice]
#jo (edit:mm)
def choose_value(field: str, label: str) -> str | None:
    values = get_field_values(MOVIES, field)
    if not values:
        print(f"Brak wartości ({label}) w kolekcji.")
        return None
    for number, value in enumerate(values, start=1):
        print(f"{number}. {value}")
    choice = get_int_input(f"Wybierz {label} [1-{len(values)}]: ", 1, len(values))
    return values[choice - 1]

#mm (edit:jo)
def filter_movies():
    field, label = choose_filter_field()
    value = choose_value(field, label)
    if value:
        display_items(filter_by_field(MOVIES, field, value))

#jo (edit:mm)
def choose_sort_field() -> tuple[str, str]:
    print("Sortuj po:")
    for number, (_, label) in SORT_FIELDS.items():
        print(f"{number}. {label.capitalize()}")
    choice = get_int_input(f"Wybierz kryterium [1-{len(SORT_FIELDS)}]: ", 1, len(SORT_FIELDS))
    return SORT_FIELDS[choice]

#jo (edit:mm)
def choose_sort_order() -> bool:
    print("Kolejność:")
    for number, (label, _) in SORT_ORDERS.items():
        print(f"{number}. {label.capitalize()}")
    choice = get_int_input(f"Wybierz kolejność [1-{len(SORT_ORDERS)}]: ", 1, len(SORT_ORDERS))
    return SORT_ORDERS[choice][1]

#jo (edit:mm)
def sort_movies():
    field, _ = choose_sort_field()
    descending = choose_sort_order()
    display_items(sort_by_field(MOVIES, field, descending))

#mm
def handle_menu_choice(choice: str) -> bool:
    match choice.strip():
        case "1":
            show_movies()
        case "2":
            add_movie()
        case "3":
            filter_movies()
        case "4":
            sort_movies()
        case "5" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case _:
            print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 5.")
    return True

#mm
def main():
    running = True
    while running:
        print_menu()
        user_choice = input("Wybierz opcję [1-5]: ")
        running = handle_menu_choice(user_choice)

#mm
if __name__ == "__main__":
    main()

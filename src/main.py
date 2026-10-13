#jo
from data import MOVIES
from services import add_item, display_items, filter_by_field, get_field_values, save_items
from validators import get_float_input, get_int_input, get_non_empty_string

#jo
FILTER_FIELDS = {
    1: ("genre", "gatunek"),
    2: ("platform", "platforma"),
}

#mm
def print_menu():
    print("\n" + "=" * 40)
    print("   CINESTREAM - KOLEKCJA FILMOWA   ")
    print("=" * 40)
    print("1. Wyświetl kolekcję")
    print("2. Dodaj film")
    print("3. Filtruj (gatunek / platforma)")
    print("4. Wyjście z programu")
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
    }

#mm (edit:jo)
def add_movie():
    added = add_item(MOVIES, read_movie_data())
    save_items(MOVIES)
    print(f"Dodano film o ID {added['id']}.")
#jo
def choose_filter_field() -> tuple[str, str]:
    print("Filtruj po:")
    for number, (_, label) in FILTER_FIELDS.items():
        print(f"{number}. {label.capitalize()}")
    choice = get_int_input(f"Wybierz kryterium [1-{len(FILTER_FIELDS)}]: ", 1, len(FILTER_FIELDS))
    return FILTER_FIELDS[choice]
#jo
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

#mm
def handle_menu_choice(choice: str) -> bool:
    match choice.strip():
        case "1":
            show_movies()
        case "2":
            add_movie()
        case "3":
            filter_movies()
        case "4" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case _:
            print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 4.")
    return True

#mm
def main():
    running = True
    while running:
        print_menu()
        user_choice = input("Wybierz opcję [1-4]: ")
        running = handle_menu_choice(user_choice)

#mm
if __name__ == "__main__":
    main()

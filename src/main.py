from data import MOVIES
from services import add_item, display_items, filter_by_genre
from validators import get_int_input, get_non_empty_string


def print_menu():
    print("\n" + "=" * 40)
    print("   CINESTREAM - KOLEKCJA FILMOWA   ")
    print("=" * 40)
    print("1. Wyswietl kolekcje")
    print("2. Dodaj film")
    print("3. Filtruj po gatunku")
    print("4. Wyjscie z programu")
    print("-" * 40)


def add_movie():
    new_movie = {
        "title": get_non_empty_string("Tytul: "),
        "genre": get_non_empty_string("Gatunek: "),
        "platform": get_non_empty_string("Platforma VOD: "),
        "rating": get_int_input("Ocena [1-10]: ", 1, 10),
    }
    added = add_item(MOVIES, new_movie)
    print(f"Dodano film o ID {added['id']}.")


def filter_movies():
    genre = get_non_empty_string("Podaj gatunek: ")
    display_items(filter_by_genre(MOVIES, genre))


def handle_menu_choice(choice: str) -> bool:
    match choice.strip():
        case "1":
            display_items(MOVIES)
        case "2":
            add_movie()
        case "3":
            filter_movies()
        case "4" | "q" | "exit":
            print("Zamykanie programu do widzenia.")
            return False
        case _:
            print("Blad: Nieznana opcja. Wybierż wartosc od 1 do 4.")
    return True


def main():
    running = True
    while running:
        print_menu()
        user_choice = input("Wybierz opcje [1-4]: ")
        running = handle_menu_choice(user_choice)


if __name__ == "__main__":
    main()
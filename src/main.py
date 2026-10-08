from data import MOVIES
from services import add_item, display_items, filter_by_genre, get_genres, save_items
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

def read_movie_data() -> dict:
    return {
        "title": get_non_empty_string("Tytuł: "),
        "genre": get_non_empty_string("Gatunek: "),
        "platform": get_non_empty_string("Platforma VOD: "),
        "rating": get_int_input("Ocena [1-10]: ", 1, 10),
    }

def add_movie():
    added = add_item(MOVIES, read_movie_data())
    save_items(MOVIES)
    print(f"Dodano film o ID {added['id']}.")


def choose_genre() -> str | None:
    genres = get_genres(MOVIES)
    if not genres:
        print("Brak gatunków w kolekcji.")
        return None
    for number, genre in enumerate(genres, start=1):
        print(f"{number}. {genre}")
    choice = get_int_input(f"Wybierz gatunek [1-{len(genres)}]: ", 1, len(genres))
    return genres[choice - 1]


def filter_movies():
    genre = choose_genre()
    if genre:
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
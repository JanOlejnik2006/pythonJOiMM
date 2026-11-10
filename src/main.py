#jo (edit:mm)
from pymongo.errors import PyMongoError
from data import STATUS, VIEW
from db import load_movies, normalize_movies, save_movie, update_movie
from network import is_online
from services import (
    apply_view, display_items, find_by_id, get_field_values,
    next_id, search_items, suggest_title,
)
from manager import MediaCatalogManager
from models import Watchlist, media_from_dict
from storage import (
    get_cache_update_time, load_movies_cache, load_pending_movies,
    load_watchlist, save_movies_cache, save_pending_movies, save_watchlist,
)
from validators import get_date_input, get_float_input, get_int_input, get_non_empty_string, get_yes_no

#mm
WATCHLIST = load_watchlist()

#mm
def watchlist_dicts() -> list:
    return [movie.to_dict() for movie in WATCHLIST.items]

#jo
def sync_pending_movies() -> int:
    pending = load_pending_movies()
    if not pending:
        return 0
    movies = load_movies()
    synced = 0
    remaining = []
    for movie in pending:
        if find_by_id(movies, movie["id"]) is not None:
            movie["id"] = next_id(movies)
            print(f"Film {movie['title']} dostał nowe ID {movie['id']}, bo poprzednie było już zajęte.")
        try:
            save_movie(movie)
            movies.append(movie)
            synced += 1
        except PyMongoError:
            remaining.append(movie)
    save_pending_movies(remaining)
    return synced

#mm (edit:jo)
def get_movies() -> list:
    if STATUS["online"]:
        try:
            synced = sync_pending_movies()
            if synced > 0:
                print(f"Wysłano {synced} film(ów) z kolejki lokalnej do bazy.")
            movies = load_movies()
            save_movies_cache(movies)
            return movies
        except PyMongoError:
            STATUS["online"] = False
            print("Utracono połączenie z bazą, przełączam na tryb offline.")
    return normalize_movies(load_movies_cache())

#jo
def get_catalog() -> MediaCatalogManager:
    return MediaCatalogManager.from_dicts(get_movies())

#jo (edit:mm)
FILTER_FIELDS = {
    1: ("genre", "gatunek"),
    2: ("platform", "platforma"),
    3: (None, "bez filtra (pokaż wszystko)"),
}

#jo (edit:mm)
SORT_FIELDS = {
    1: ("id", "ID"),
    2: ("title", "tytuł"),
    3: ("genre", "gatunek"),
    4: ("platform", "platforma"),
    5: ("rating", "ocena"),
    6: ("duration", "czas trwania"),
    7: ("release_date", "data premiery"),
}

#jo(edit:mm)
SORT_ORDERS = {
    1: ("rosnąco", False),
    2: ("malejąco", True),
}

#jo
def print_view():
    labels = dict(SORT_FIELDS.values())
    sort_field, descending = VIEW["sort"]
    order = "malejąco" if descending else "rosnąco"
    if VIEW["filter"] is None:
        filter_text = "brak"
    else:
        field, value = VIEW["filter"]
        filter_text = f"{labels[field]} = {value}"
    print(f"Filtr: {filter_text} | Sortowanie: {labels[sort_field]} {order}")

#mm (edit:jo)
def print_status():
    status_text = "ONLINE" if STATUS["online"] else "OFFLINE"
    print(f"Status: {status_text} | Lokalny zapis: {get_cache_update_time()}")

#mm (edit:jo)
def print_menu():
    print("\n" + "=" * 40)
    print("   CINESTREAM - KOLEKCJA FILMOWA   ")
    print("=" * 40)
    print_status()
    print_view()
    print("1. Szukaj filmu")
    print("2. Watchlista")
    print("3. Wyświetl kolekcję")
    print("4. Sortuj")
    print("5. Filtruj")
    print("6. Dodaj film lub serial")
    print("7. Raport platform")
    print("8. Połącz z bazą (online)")
    print("9. Wyjście z programu")
    print("-" * 40)

#mm (edit:jo)
def show_movies():
    catalog = get_catalog()
    display_items(apply_view(catalog.as_dicts(), VIEW))
    kinds = ", ".join(f"{label}: {count}" for label, count in catalog.count_by_kind().items())
    print(
        f"Pozycji: {len(catalog)} ({kinds}) | Łączny czas: {catalog.total_runtime_hours()} h | "
        f"Waga odtwarzania: {catalog.total_playback_weight()} h"
    )

#jo
MEDIA_FORMS = {
    1: ("movie", "Film"),
    2: ("series", "Serial"),
}

#jo
def read_movie_fields() -> dict:
    return {
        "duration": get_int_input("Czas trwania [min]: ", 1, 600),
        "director": get_non_empty_string("Reżyser: "),
    }

#jo
def read_series_fields() -> dict:
    return {
        "seasons": get_int_input("Liczba sezonów: ", 1, 100),
        "episodes_per_season": get_int_input("Odcinków w sezonie: ", 1, 500),
        "minutes_per_episode": get_int_input("Minut na odcinek: ", 1, 300),
    }

#jo
FIELD_READERS = {
    "movie": read_movie_fields,
    "series": read_series_fields,
}

#mm (edit:jo)
def read_media_data() -> dict:
    print("Co dodajesz?")
    for number, (_, label) in MEDIA_FORMS.items():
        print(f"{number}. {label}")
    choice = get_int_input(f"Wybierz [1-{len(MEDIA_FORMS)}]: ", 1, len(MEDIA_FORMS))
    type_tag = MEDIA_FORMS[choice][0]
    media_data = {
        "type": type_tag,
        "title": get_non_empty_string("Tytuł: "),
        "genre": get_non_empty_string("Gatunek: "),
        "platform": get_non_empty_string("Platforma VOD: "),
    }
    media_data.update(FIELD_READERS[type_tag]())
    media_data["release_date"] = get_date_input("Data premiery [RRRR-MM-DD]: ")
    media_data["is_watched"] = get_yes_no("Czy jest już obejrzany? [t/n]: ")
    if media_data["is_watched"]:
        media_data["rating"] = get_float_input("Ocena [1-10, np. 7.5]: ", 1, 10)
    else:
        media_data["rating"] = None
    return media_data

#mm (edit:jo)
def add_movie():
    media_data = read_media_data()
    catalog = get_catalog()
    media = media_from_dict({"id": catalog.next_id(), **media_data})
    catalog.add(media)
    added = media.to_dict()
    save_movies_cache(catalog.as_dicts())
    if STATUS["online"]:
        try:
            save_movie(added)
            print(f"Dodano: {media.kind_label()} {media.title} (ID {media.title_id}).")
            return
        except PyMongoError:
            STATUS["online"] = False
            print("Utracono połączenie z bazą.")
    pending = load_pending_movies()
    pending.append(added)
    save_pending_movies(pending)
    print(f"Zapisano lokalnie: {media.kind_label()} {media.title} (ID {media.title_id}). Zostanie wysłany na serwer po połączeniu z internetem.")
#mm (edit:jo)
def search_movies():
    query = get_non_empty_string("Szukaj (tytuł, gatunek lub platforma): ")
    movies = apply_view(get_catalog().as_dicts(), VIEW)
    results = search_items(movies, query)
    if not results:
        print(f"Brak filmów dla frazy '{query}'.")
        suggestion = suggest_title(movies, query)
        if suggestion:
            print(f"Czy chodziło o: {suggestion}?")
        return
    display_items(results)

#jo (edit:mm)
def choose_filter_field() -> tuple[str, str]:
    print("Filtruj po:")
    for number, (_, label) in FILTER_FIELDS.items():
        print(f"{number}. {label.capitalize()}")
    choice = get_int_input(f"Wybierz kryterium [1-{len(FILTER_FIELDS)}]: ", 1, len(FILTER_FIELDS))
    return FILTER_FIELDS[choice]
#jo (edit:mm)
def choose_value(items_list: list, field: str, label: str) -> str | None:
    values = get_field_values(items_list, field)
    if not values:
        print(f"Brak wartości ({label}) w kolekcji.")
        return None
    for number, value in enumerate(values, start=1):
        print(f"{number}. {value}")
    choice = get_int_input(f"Wybierz {label} [1-{len(values)}]: ", 1, len(values))
    return values[choice - 1]

#mm (edit:jo)
def filter_movies(items_list: list):
    field, label = choose_filter_field()
    if field is None:
        VIEW["filter"] = None
    else:
        value = choose_value(items_list, field, label)
        if value is None:
            return
        VIEW["filter"] = (field, value)
    display_items(apply_view(items_list, VIEW))

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
def sort_movies(items_list: list):
    field, _ = choose_sort_field()
    VIEW["sort"] = (field, choose_sort_order())
    display_items(apply_view(items_list, VIEW))

#mm
def print_watchlist_menu():
    print("\n--- WATCHLISTA ---")
    print_view()
    print("1. Wyświetl watchlistę")
    print("2. Dodaj film do watchlisty")
    print("3. Usuń film z watchlisty")
    print("4. Oznacz jako obejrzany i oceń")
    print("5. Filtruj")
    print("6. Sortuj")
    print("7. Powrót do menu")

#mm
def show_watchlist():
    visible = apply_view(watchlist_dicts(), VIEW)
    display_items(visible)
    shown = Watchlist(items=[media_from_dict(movie) for movie in visible])
    minutes = shown.total_minutes()
    print(f"Łączny czas seansu: {minutes // 60} h {minutes % 60} min ({shown.total_runtime_hours()} h)")
    print(f"Średnia ocena obejrzanych: {shown.average_rating():.1f}")

#mm
def choose_movie(items_list: list) -> dict | None:
    items_list = apply_view(items_list, VIEW)
    if not items_list:
        print("Brak filmów do wyboru.")
        return None
    for number, item in enumerate(items_list, start=1):
        print(f"{number}. {item['title']} ({item['duration']} min)")
    print("0. Anuluj")
    choice = get_int_input(f"Wybierz film [0-{len(items_list)}]: ", 0, len(items_list))
    if choice == 0:
        print("Anulowano.")
        return None
    return items_list[choice - 1]

#mm (edit:jo)
def watchlist_add():
    movies = get_catalog().as_dicts()
    movie = choose_movie(movies)
    if movie is None:
        return
    if WATCHLIST.add(media_from_dict(movie)):
        save_watchlist(WATCHLIST)
        print(f"Dodano film {movie['title']} do watchlisty.")
    else:
        print(f"Błąd: Film {movie['title']} już jest na watchliście.")

#mm
def watchlist_remove():
    movie = choose_movie(watchlist_dicts())
    if movie is None:
        return
    WATCHLIST.remove(movie["id"])
    save_watchlist(WATCHLIST)
    print(f"Usunięto film {movie['title']} z watchlisty.")

#mm
def watchlist_rate():
    movie = choose_movie(watchlist_dicts())
    if movie is None:
        return
    rating = get_float_input("Ocena [1-10, np. 7.5]: ", 1, 10)
    rated = WATCHLIST.mark_watched(movie["id"], rating)
    save_watchlist(WATCHLIST)
    print(f"Film {rated.title} oznaczono jako obejrzany z oceną {rated.rating}.")
    if not STATUS["online"]:
        print("Brak internetu – ocena zapisana tylko na watchliście, w bazie jej jeszcze nie ma.")
        return
    try:
        update_movie(rated.to_dict())
        print("Ocena zapisana też w bazie.")
    except PyMongoError:
        STATUS["online"] = False
        print("Utracono połączenie z bazą – ocena zapisana tylko na watchliście.")

#mm
def watchlist_menu():
    running = True
    while running:
        print_watchlist_menu()
        match input("Wybierz opcję [1-7]: ").strip():
            case "1":
                show_watchlist()
            case "2":
                watchlist_add()
            case "3":
                watchlist_remove()
            case "4":
                watchlist_rate()
            case "5":
                filter_movies(watchlist_dicts())
            case "6":
                sort_movies(watchlist_dicts())
            case "7":
                running = False
            case _:
                print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 7.")

#mm
def show_platform_report():
    catalog = get_catalog()
    report = catalog.platform_report()
    if not report:
        print("Brak pozycji do raportu.")
        return
    width = max(len("Platforma"), max(len(row["platforma"]) for row in report))
    header = f"{'Platforma':<{width}} {'Pozycji':>7} {'Śr. ocena':>9} {'Czas [h]':>9}"
    print(header)
    print("-" * len(header))
    for row in report:
        rating = f"{row['srednia_ocena']:.2f}" if row["srednia_ocena"] is not None else "-"
        print(f"{row['platforma']:<{width}} {row['pozycji']:>7} {rating:>9} {row['laczny_czas_h']:>9.2f}")
    print(f"Razem: {len(catalog)} pozycji, {catalog.total_runtime_hours()} h")

#mm
def handle_menu_choice(choice: str) -> bool:
    match choice.strip():
        case "1":
            search_movies()
        case "2":
            watchlist_menu()
        case "3":
            show_movies()
        case "4":
            sort_movies(get_catalog().as_dicts())
        case "5":
            filter_movies(get_catalog().as_dicts())
        case "6":
            add_movie()
        case "7":
            show_platform_report()
        case "8":
            reconnect()
        case "9" | "q" | "exit":
            print("Zamykanie programu. Do widzenia!")
            return False
        case _:
            print("Błąd: Nieznana opcja. Wybierz wartość od 1 do 9.")
    return True

#mm (edit:jo)
def reconnect():
    if not is_online():
        print("Błąd: Nadal brak połączenia z internetem.")
        return
    try:
        synced = sync_pending_movies()
        if synced > 0:
            print(f"Wysłano {synced} film(ów) z kolejki lokalnej do bazy.")
        movies = load_movies()
        save_movies_cache(movies)
        STATUS["online"] = True
        print("Połączono z bazą MongoDB. Tryb ONLINE aktywny.")
    except PyMongoError:
        STATUS["online"] = False
        print("Błąd: Internet działa, ale baza MongoDB nie odpowiada.")

#jo (edit:mm)
def print_offline_info():
    print("Brak połączenia z internetem. Działasz w trybie offline.")
    print("Filmy są wczytywane z ostatniej kopii zapisanej na dysku.")

#mm (edit:jo)
def main():
    STATUS["online"] = is_online()
    if not STATUS["online"]:
        print_offline_info()
    running = True
    while running:
        print_menu()
        user_choice = input("Wybierz opcję [1-9]: ")
        try:
            running = handle_menu_choice(user_choice)
        except PyMongoError:
            STATUS["online"] = False
            print_offline_info()

#mm
if __name__ == "__main__":
    main()

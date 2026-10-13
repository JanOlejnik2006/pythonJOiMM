#jo
import os
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.py")

#mm
def format_header() -> str:
    header = f"{'ID':<4} {'Tytuł':<20} {'Gatunek':<14} {'Platforma':<12} {'Ocena':>5}"
    return header + "\n" + "-" * 58

#jo
HIT_THRESHOLD = 9

#mm (edit:jo)
def format_row(item: dict) -> str:
    row = (
        f"{item['id']:<4} {item['title']:<20} {item['genre']:<14} "
        f"{item['platform']:<12} {item['rating']:>5.1f}"
    )
    if item["rating"] >= HIT_THRESHOLD:
        row += "  HIT"
    return row

#mm
def display_items(items_list: list) -> None:
    if not items_list:
        print("Brak pozycji do wyświetlenia.")
        return
    print(format_header())
    for item in items_list:
        print(format_row(item))

#jo
def next_id(items_list: list) -> int:
    return max((item["id"] for item in items_list), default=0) + 1

#jo
def add_item(items_list: list, new_item_data: dict) -> dict:
    item = {"id": next_id(items_list), **new_item_data}
    items_list.append(item)
    return item

#jo
def filter_by_field(items_list: list, field: str, value: str) -> list:
    return [item for item in items_list if item[field].lower() == value.lower()]

#jo
def sort_by_field(items_list: list, field: str, descending: bool = False) -> list:
    return sorted(
        items_list,
        key=lambda item: item[field].lower() if isinstance(item[field], str) else item[field],
        reverse=descending,
    )

#jo
def get_field_values(items_list: list, field: str) -> list:
    return sorted({item[field] for item in items_list})

#jo
def filter_by_genre(items_list: list, genre: str) -> list:
    return filter_by_field(items_list, "genre", genre)

#jo
def get_genres(items_list: list) -> list:
    return get_field_values(items_list, "genre")
#jo
def filter_by_platform(items_list: list, platform: str) -> list:
    return filter_by_field(items_list, "platform", platform)
#jo
def get_platforms(items_list: list) -> list:
    return get_field_values(items_list, "platform")

#jo
def save_items(items_list: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        file.write("MOVIES = [\n")
        for item in items_list:
            file.write(f"    {item!r},\n")
        file.write("]\n")
        
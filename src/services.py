#jo
import os
DATA_FILE = os.path.join(os.path.dirname(__file__), "data.py")

#mm
def column_widths(items_list: list) -> dict:
    widths = {"title": len("Tytuł"), "genre": len("Gatunek"), "platform": len("Platforma")}
    for item in items_list:
        for field in widths:
            widths[field] = max(widths[field], len(item[field]))
    return widths

#mm
def format_header(widths: dict) -> str:
    header = (
        f"{'ID':<4} {'Tytuł':<{widths['title']}} {'Gatunek':<{widths['genre']}} "
        f"{'Platforma':<{widths['platform']}} {'Czas':>7} {'Ocena':>5}"
    )
    return header + "\n" + "-" * len(header)

#jo
HIT_THRESHOLD = 9

#mm (edit:jo)
def format_row(item: dict, widths: dict) -> str:
    row = (
        f"{item['id']:<4} {item['title']:<{widths['title']}} {item['genre']:<{widths['genre']}} "
        f"{item['platform']:<{widths['platform']}} {item['duration']:>3} min {item['rating']:>5.1f}"
    )
    if item["rating"] >= HIT_THRESHOLD:
        row += "  HIT"
    return row

#mm
def display_items(items_list: list) -> None:
    if not items_list:
        print("Brak pozycji do wyświetlenia.")
        return
    widths = column_widths(items_list)
    print(format_header(widths))
    for item in items_list:
        print(format_row(item, widths))

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
def apply_view(items_list: list, view: dict) -> list:
    if view["filter"] is not None:
        field, value = view["filter"]
        items_list = filter_by_field(items_list, field, value)
    field, descending = view["sort"]
    return sort_by_field(items_list, field, descending)

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
def find_by_id(items_list: list, item_id: int) -> dict | None:
    for item in items_list:
        if item["id"] == item_id:
            return item
    return None

#jo
def add_to_watchlist(watchlist: list, items_list: list, item_id: int) -> bool:
    item = find_by_id(items_list, item_id)
    if item is None or find_by_id(watchlist, item_id) is not None:
        return False
    watchlist.append(dict(item))
    return True

#jo
def remove_from_watchlist(watchlist: list, item_id: int) -> bool:
    item = find_by_id(watchlist, item_id)
    if item is None:
        return False
    watchlist.remove(item)
    return True

#jo
def total_duration(items_list: list) -> int:
    return sum(item["duration"] for item in items_list)

#jo (edit:mm)
def save_watchlist(items_list: list) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        file.write("WATCHLIST = [\n")
        for item in items_list:
            file.write(f"    {item!r},\n")
        file.write("]\n")
        
#mm
import difflib

#jo
POLISH_LETTERS = str.maketrans("ąćęłńóśźż", "acelnoszz")

#jo
def normalize_text(text: str) -> str:
    return text.casefold().translate(POLISH_LETTERS)

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

#mm (edit:jo)
def search_items(items_list: list, query: str) -> list:
    words = normalize_text(query).split()
    results = []
    for item in items_list:
        text = normalize_text(f"{item['title']} {item['genre']} {item['platform']}")
        if all(word in text for word in words):
            results.append(item)
    return results

#mm
def suggest_title(items_list: list, query: str) -> str | None:
    titles = {normalize_text(item["title"]): item["title"] for item in items_list}
    matches = difflib.get_close_matches(normalize_text(query), titles, n=1, cutoff=0.6)
    if not matches:
        return None
    return titles[matches[0]]

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

#mm
def platform_summary(items_list: list) -> list:
    summary = []
    for platform in get_field_values(items_list, "platform"):
        ratings = [item["rating"] for item in items_list if item["platform"] == platform]
        summary.append({
            "platforma": platform,
            "liczba_filmow": len(ratings),
            "srednia_ocena": round(sum(ratings) / len(ratings), 2),
            "najnizsza_ocena": float(min(ratings)),
            "najwyzsza_ocena": float(max(ratings)),
        })
    return summary

#jo
def total_duration(items_list: list) -> int:
    return sum(item["duration"] for item in items_list)

#mm
def average_rating(items_list: list) -> float:
    if not items_list:
        return 0.0
    return sum(item["rating"] for item in items_list) / len(items_list)

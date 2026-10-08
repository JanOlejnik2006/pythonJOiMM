def display_items(items_list: list) -> None:
    if not items_list:
        print("Brak pozycji do wyświetlenia.")
        return
    print(f"{'ID':<4} {'Tytuł':<20} {'Gatunek':<14} {'Platforma':<12} {'Ocena':>5}")
    print("-" * 58)
    for item in items_list:
        print(
            f"{item['id']:<4} {item['title']:<20} {item['genre']:<14} "
            f"{item['platform']:<12} {item['rating']:>5}"
        )


def add_item(items_list: list, new_item_data: dict) -> dict:
    new_id = max((item["id"] for item in items_list), default=0) + 1
    item = {"id": new_id, **new_item_data}
    items_list.append(item)
    return item


def filter_by_genre(items_list: list, genre: str) -> list:
    return [item for item in items_list if item["genre"].lower() == genre.lower()]
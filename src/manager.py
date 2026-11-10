#mm
from models import MediaTitle, media_from_dict

#mm
class MediaCatalogManager:
    """Menedżer kolekcji: wszystkie operacje na filmach i serialach w jednym miejscu."""

    def __init__(self, items: list[MediaTitle] | None = None) -> None:
        self._catalog: list[MediaTitle] = []
        for item in items if items is not None else []:
            self.add(item)

    @classmethod
    def from_dicts(cls, rows: list) -> "MediaCatalogManager":
        """Odtwarza kolekcję ze słowników (np. z bazy albo z JSON) przez fabrykę typów."""
        return cls([media_from_dict(row) for row in rows])

    @property
    def items(self) -> list[MediaTitle]:
        return list(self._catalog)

    def add(self, media: MediaTitle) -> None:
        if not isinstance(media, MediaTitle):
            raise TypeError("Kolekcja przyjmuje tylko obiekty klas pochodnych MediaTitle.")
        if self.find(media.title_id) is not None:
            raise ValueError(f"Pozycja o ID {media.title_id} już jest w kolekcji.")
        self._catalog.append(media)

    def find(self, title_id: int) -> MediaTitle | None:
        for media in self._catalog:
            if media.title_id == title_id:
                return media
        return None

    def next_id(self) -> int:
        return max((media.title_id for media in self._catalog), default=0) + 1

    def as_dicts(self) -> list:
        return [media.to_dict() for media in self._catalog]

    def __len__(self) -> int:
        return len(self._catalog)

    def total_runtime_minutes(self) -> int:
        """Polimorfizm: każda pozycja sama wie, ile trwa."""
        return sum(media.runtime_minutes() for media in self._catalog)

    def total_runtime_hours(self) -> float:
        return round(self.total_runtime_minutes() / 60, 2)

    def total_playback_weight(self) -> float:
        return round(sum(media.calculate_playback_weight() for media in self._catalog), 2)

    def count_by_kind(self) -> dict:
        counts = {}
        for media in self._catalog:
            label = media.kind_label()
            counts[label] = counts.get(label, 0) + 1
        return counts

    def platform_report(self) -> list:
        """Raport platform: liczba pozycji, średnia ocen obejrzanych i łączny czas – bez sprawdzania typów."""
        report = []
        for platform in sorted({media.platform for media in self._catalog}):
            on_platform = [media for media in self._catalog if media.platform == platform]
            ratings = [media.rating for media in on_platform if media.rating is not None]
            report.append({
                "platforma": platform,
                "pozycji": len(on_platform),
                "srednia_ocena": round(sum(ratings) / len(ratings), 2) if ratings else None,
                "laczny_czas_min": sum(media.runtime_minutes() for media in on_platform),
            })
        return report

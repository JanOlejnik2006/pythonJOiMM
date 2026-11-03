#mm
from datetime import datetime

#mm
class MediaTitle:
    """Pojedynczy film w kolekcji CineStream."""

    __slots__ = ("_title_id", "title", "genre", "platform", "_duration_min", "_release_date", "_is_watched", "_rating")

    def __init__(
        self,
        title_id: int,
        title: str,
        genre: str,
        platform: str,
        duration_min: int,
        release_date: str = "-",
        is_watched: bool = False,
        rating: float | None = None,
    ) -> None:
        self._title_id: int = title_id
        self.title: str = title
        self.genre: str = genre
        self.platform: str = platform
        self.duration_min = duration_min
        self.release_date = release_date
        self._is_watched: bool = False
        self._rating: float | None = None
        self.is_watched = is_watched
        self.rating = rating

    @property
    def title_id(self) -> int:
        """ID jest tylko do odczytu – nie ma settera."""
        return self._title_id

    @property
    def duration_min(self) -> int:
        return self._duration_min

    @duration_min.setter
    def duration_min(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Czas trwania musi być liczbą minut >= 0 (podano: {value}).")
        self._duration_min = value

    @property
    def release_date(self) -> str:
        return self._release_date

    @release_date.setter
    def release_date(self, value: str) -> None:
        if value != "-":
            try:
                datetime.strptime(value, "%Y-%m-%d")
            except (ValueError, TypeError):
                raise ValueError(f"Data premiery musi mieć format RRRR-MM-DD (podano: {value}).")
        self._release_date = value

    @property
    def year(self) -> int | None:
        """Rok premiery wyliczany z daty premiery."""
        if self._release_date == "-":
            return None
        return int(self._release_date[:4])

    @property
    def is_watched(self) -> bool:
        return self._is_watched

    @is_watched.setter
    def is_watched(self, value: bool) -> None:
        if not isinstance(value, bool):
            raise TypeError("Pole is_watched musi być wartością True albo False.")
        self._is_watched = value
        if not value:
            self._rating = None

    @property
    def rating(self) -> float | None:
        return self._rating

    @rating.setter
    def rating(self, value: float | None) -> None:
        """Niezmiennik: ocenę można dać tylko obejrzanemu filmowi."""
        if value is None:
            self._rating = None
            return
        if not self._is_watched:
            raise ValueError("Nie można ocenić filmu, który nie jest obejrzany.")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError("Ocena musi być liczbą.")
        if not 1.0 <= value <= 10.0:
            raise ValueError(f"Ocena musi być w zakresie 1.0-10.0 (podano: {value}).")
        self._rating = round(float(value), 1)

    def mark_watched(self, rating: float) -> None:
        """Oznacza film jako obejrzany i od razu go ocenia."""
        self.is_watched = True
        self.rating = rating

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

    #jo
    def __repr__(self) -> str:
        return (
            f"MediaTitle(title_id={self.title_id}, title={self.title!r}, genre={self.genre!r}, "
            f"platform={self.platform!r}, duration_min={self.duration_min}, "
            f"release_date={self.release_date!r}, is_watched={self.is_watched}, rating={self.rating})"
        )

    #jo
    def __str__(self) -> str:
        year = self.year if self.year is not None else "-"
        rating = f"{self.rating:.1f}" if self.rating is not None else "-"
        return f"[{self.title_id:02d}] {self.title} ({year}) | {self.genre} | {self.duration_min} min | ocena: {rating}"

    #jo
    def __eq__(self, other: object) -> bool:
        """Dwa filmy są tym samym filmem, jeśli mają to samo ID."""
        if not isinstance(other, MediaTitle):
            return False
        return self.title_id == other.title_id

    #jo
    def __lt__(self, other: "MediaTitle") -> bool:
        """Naturalny porządek: najpierw ocenione, od najwyższej oceny, potem po tytule."""
        if not isinstance(other, MediaTitle):
            return NotImplemented
        return self._sort_key() < other._sort_key()

    #jo
    def _sort_key(self) -> tuple:
        rating = self.rating if self.rating is not None else 0.0
        return (self.rating is None, -rating, self.title.lower())

    #jo
    def to_dict(self) -> dict:
        return {
            "id": self.title_id,
            "title": self.title,
            "genre": self.genre,
            "platform": self.platform,
            "duration": self.duration_min,
            "release_date": self.release_date,
            "is_watched": self.is_watched,
            "rating": self.rating,
        }

    #jo
    @classmethod
    def from_dict(cls, data: dict) -> "MediaTitle":
        is_watched = bool(data.get("is_watched", False))
        return cls(
            title_id=int(data["id"]),
            title=str(data["title"]),
            genre=str(data.get("genre", "brak")),
            platform=str(data.get("platform", "brak")),
            duration_min=int(data.get("duration", 0)),
            release_date=str(data.get("release_date", "-")),
            is_watched=is_watched,
            rating=data.get("rating") if is_watched else None,
        )

#mm
class Watchlist:
    """Agregat: lista filmów do obejrzenia, która pilnuje własnej spójności."""

    __slots__ = ("name", "_items")

    def __init__(self, name: str = "Do obejrzenia", items: list[MediaTitle] | None = None) -> None:
        self.name: str = name
        self._items: list[MediaTitle] = []
        for item in items if items is not None else []:
            self.add(item)

    @property
    def items(self) -> list[MediaTitle]:
        """Zwraca kopię listy, żeby nie dało się jej zmienić z pominięciem metod."""
        return list(self._items)

    def add(self, movie: MediaTitle) -> bool:
        if not isinstance(movie, MediaTitle):
            raise TypeError("Na watchliście mogą być tylko obiekty MediaTitle.")
        if movie in self._items:
            return False
        self._items.append(movie)
        return True

    def remove(self, title_id: int) -> bool:
        movie = self.find(title_id)
        if movie is None:
            return False
        self._items.remove(movie)
        return True

    def find(self, title_id: int) -> MediaTitle | None:
        for movie in self._items:
            if movie.title_id == title_id:
                return movie
        return None

    def total_minutes(self) -> int:
        return sum(movie.duration_min for movie in self._items)

    def total_runtime_hours(self) -> float:
        return round(self.total_minutes() / 60, 2)

    def average_rating(self) -> float:
        ratings = [movie.rating for movie in self._items if movie.rating is not None]
        if not ratings:
            return 0.0
        return round(sum(ratings) / len(ratings), 1)

    def __len__(self) -> int:
        return len(self._items)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Watchlist):
            return False
        return self.name == other.name and self._items == other._items

    def __repr__(self) -> str:
        return f"Watchlist(name={self.name!r}, items={self._items!r})"

    def __str__(self) -> str:
        lines = [f"=== {self.name.upper()} ({len(self)} filmów) ==="]
        lines.extend(f"  * {movie}" for movie in self._items)
        lines.append(f"  ŁĄCZNIE: {self.total_runtime_hours()} h")
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "items": [movie.to_dict() for movie in self._items],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Watchlist":
        movies = [MediaTitle.from_dict(raw) for raw in data.get("items", [])]
        return cls(str(data.get("name", "Do obejrzenia")), movies)

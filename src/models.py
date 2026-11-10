#mm (edit:jo)
import math
from abc import ABC, abstractmethod
from datetime import datetime

#mm
class MediaTitle(ABC):
    """Klasa bazowa: wspólne pola i kontrakt dla filmu i serialu."""

    __slots__ = ("_title_id", "title", "genre", "platform", "_release_date", "_is_watched", "_rating")
    TYPE_TAG: str = ""

    def __init__(
        self,
        title_id: int,
        title: str,
        genre: str,
        platform: str,
        release_date: str = "-",
        is_watched: bool = False,
        rating: float | None = None,
    ) -> None:
        self._title_id: int = title_id
        self.title: str = title
        self.genre: str = genre
        self.platform: str = platform
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
        """Niezmiennik: ocenę można dać tylko obejrzanej pozycji."""
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
        """Oznacza pozycję jako obejrzaną i od razu ją ocenia."""
        self.is_watched = True
        self.rating = rating

    @abstractmethod
    def runtime_minutes(self) -> int:
        """Łączny czas oglądania w minutach – każda podklasa liczy go po swojemu."""

    @abstractmethod
    def calculate_playback_weight(self) -> float:
        """Waga odtwarzania w godzinach – każda podklasa liczy ją po swojemu."""

    @abstractmethod
    def kind_label(self) -> str:
        """Nazwa rodzaju pozycji wyświetlana w menu."""

    #jo
    def __str__(self) -> str:
        year = self.year if self.year is not None else "-"
        rating = f"{self.rating:.1f}" if self.rating is not None else "-"
        return (
            f"[{self.title_id:02d}] {self.kind_label()}: {self.title} ({year}) | {self.genre} | "
            f"{self.runtime_minutes()} min | ocena: {rating}"
        )

    #jo
    def __eq__(self, other: object) -> bool:
        """Dwie pozycje są tą samą pozycją, jeśli mają to samo ID."""
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

    #jo (edit:mm)
    def to_dict(self) -> dict:
        """Wspólna część słownika – podklasy dopisują swoje pola, a "type" mówi, jaka to klasa."""
        return {
            "type": self.TYPE_TAG,
            "id": self.title_id,
            "title": self.title,
            "genre": self.genre,
            "platform": self.platform,
            "release_date": self.release_date,
            "is_watched": self.is_watched,
            "rating": self.rating,
        }


#mm
class Movie(MediaTitle):
    """Film: ma jeden czas trwania i reżysera."""

    __slots__ = ("_duration_min", "director")
    TYPE_TAG = "movie"

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
        director: str = "nieznany",
    ) -> None:
        super().__init__(title_id, title, genre, platform, release_date, is_watched, rating)
        self.duration_min = duration_min
        self.director: str = director

    @property
    def duration_min(self) -> int:
        return self._duration_min

    @duration_min.setter
    def duration_min(self, value: int) -> None:
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Czas trwania musi być liczbą minut >= 0 (podano: {value}).")
        self._duration_min = value

    def runtime_minutes(self) -> int:
        return self.duration_min

    def calculate_playback_weight(self) -> float:
        """Film ogląda się na jeden raz, więc waga to po prostu czas w godzinach."""
        return round(self.duration_min / 60, 2)

    def kind_label(self) -> str:
        return "Film"

    def __repr__(self) -> str:
        return (
            f"Movie(title_id={self.title_id}, title={self.title!r}, genre={self.genre!r}, "
            f"platform={self.platform!r}, duration_min={self.duration_min}, "
            f"release_date={self.release_date!r}, is_watched={self.is_watched}, "
            f"rating={self.rating}, director={self.director!r})"
        )

    def __str__(self) -> str:
        """Opis z klasy bazowej (super) + to, co ma tylko film: reżyser."""
        return f"{super().__str__()} | reż. {self.director}"

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["duration"] = self.duration_min
        data["director"] = self.director
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Movie":
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
            director=str(data.get("director", "nieznany")),
        )


#jo
class Series(MediaTitle):
    """Serial: czas liczony z sezonów, odcinków i długości odcinka."""

    __slots__ = ("_seasons", "_episodes_per_season", "_minutes_per_episode")
    TYPE_TAG = "series"
    INTRO_MINUTES = 5

    def __init__(
        self,
        title_id: int,
        title: str,
        genre: str,
        platform: str,
        seasons: int,
        episodes_per_season: int,
        minutes_per_episode: int,
        release_date: str = "-",
        is_watched: bool = False,
        rating: float | None = None,
    ) -> None:
        super().__init__(title_id, title, genre, platform, release_date, is_watched, rating)
        self._seasons = self._positive_int(seasons, "Liczba sezonów")
        self._episodes_per_season = self._positive_int(episodes_per_season, "Liczba odcinków w sezonie")
        self._minutes_per_episode = self._positive_int(minutes_per_episode, "Długość odcinka")

    @staticmethod
    def _positive_int(value: int, label: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"{label} musi być liczbą całkowitą większą od zera (podano: {value}).")
        return value

    @property
    def seasons(self) -> int:
        return self._seasons

    @property
    def episodes_per_season(self) -> int:
        return self._episodes_per_season

    @property
    def minutes_per_episode(self) -> int:
        return self._minutes_per_episode

    def episodes_total(self) -> int:
        return self._seasons * self._episodes_per_season

    def runtime_minutes(self) -> int:
        return self.episodes_total() * self._minutes_per_episode

    def calculate_playback_weight(self) -> float:
        """Serial ogląda się w odcinkach, więc doliczamy czołówkę i podsumowanie każdego odcinka."""
        return round(self.episodes_total() * (self._minutes_per_episode + self.INTRO_MINUTES) / 60, 2)

    def kind_label(self) -> str:
        return "Serial"

    def days_to_finish(self, minutes_per_day: int = 60) -> int:
        """Tylko serial: ile dni zajmie obejrzenie całości przy danej liczbie minut dziennie (zaokrąglamy w górę)."""
        minutes_per_day = self._positive_int(minutes_per_day, "Liczba minut dziennie")
        return math.ceil(self.runtime_minutes() / minutes_per_day)

    def __repr__(self) -> str:
        return (
            f"Series(title_id={self.title_id}, title={self.title!r}, genre={self.genre!r}, "
            f"platform={self.platform!r}, seasons={self.seasons}, "
            f"episodes_per_season={self.episodes_per_season}, minutes_per_episode={self.minutes_per_episode}, "
            f"release_date={self.release_date!r}, is_watched={self.is_watched}, rating={self.rating})"
        )

    def __str__(self) -> str:
        """Opis z klasy bazowej (super) + to, co ma tylko serial: sezony, odcinki i dni do końca."""
        return (
            f"{super().__str__()} | {self.seasons} sez. x {self.episodes_per_season} odc. | "
            f"{self.days_to_finish()} dni po 60 min"
        )

    def to_dict(self) -> dict:
        data = super().to_dict()
        data["seasons"] = self.seasons
        data["episodes_per_season"] = self.episodes_per_season
        data["minutes_per_episode"] = self.minutes_per_episode
        data["duration"] = self.runtime_minutes()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "Series":
        is_watched = bool(data.get("is_watched", False))
        return cls(
            title_id=int(data["id"]),
            title=str(data["title"]),
            genre=str(data.get("genre", "brak")),
            platform=str(data.get("platform", "brak")),
            seasons=int(data["seasons"]),
            episodes_per_season=int(data["episodes_per_season"]),
            minutes_per_episode=int(data["minutes_per_episode"]),
            release_date=str(data.get("release_date", "-")),
            is_watched=is_watched,
            rating=data.get("rating") if is_watched else None,
        )


#jo
MEDIA_REGISTRY: dict[str, type[MediaTitle]] = {
    "movie": Movie,
    "series": Series,
}

#jo
def media_from_dict(data: dict) -> MediaTitle:
    """Fabryka: wybiera klasę po polu "type" bez drabinki if/elif. Stare wpisy bez typu to filmy."""
    type_tag = data.get("type", "movie")
    target_cls = MEDIA_REGISTRY.get(type_tag)
    if target_cls is None:
        raise ValueError(f"Nieznany typ pozycji w danych: {type_tag!r}")
    return target_cls.from_dict(data)


#mm
class Watchlist:
    """Agregat: lista filmów i seriali do obejrzenia, która pilnuje własnej spójności."""

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
            raise TypeError("Na watchliście mogą być tylko obiekty klas pochodnych MediaTitle.")
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

    def mark_watched(self, title_id: int, rating: float) -> MediaTitle | None:
        """Oznacza film z listy jako obejrzany i ocenia go przez metodę agregatu."""
        movie = self.find(title_id)
        if movie is None:
            return None
        movie.mark_watched(rating)
        return movie

    def total_minutes(self) -> int:
        return sum(movie.runtime_minutes() for movie in self._items)

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
        movies = [media_from_dict(raw) for raw in data.get("items", [])]
        return cls(str(data.get("name", "Do obejrzenia")), movies)

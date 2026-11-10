#jo
import os
from dotenv import load_dotenv
from pymongo import MongoClient
from models import Movie

#jo
load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000, connect=False)
collection = client[os.getenv("MONGO_DB")]["movies"]

#mm
DEFAULT_FIELDS = {
    "title": "bez tytułu",
    "genre": "brak",
    "platform": "brak",
    "rating": 0.0,
    "duration": 0,
    "release_date": "-",
    "is_watched": False,
}

#jo
def normalize_movies(raw_movies: list) -> list:
    movies = []
    for raw in raw_movies:
        try:
            movies.append(Movie.from_dict({**DEFAULT_FIELDS, **raw}).to_dict())
        except (KeyError, ValueError, TypeError):
            print(f"[OSTRZEŻENIE] Pominięto błędny wpis filmu: {raw.get('title', '?')}")
    return movies

#jo (edit:mm)
def load_movies() -> list:
    return normalize_movies(list(collection.find({}, {"_id": 0})))

#jo
def save_movie(movie: dict) -> None:
    collection.insert_one(dict(movie))

#jo
def update_movie(movie: dict) -> None:
    collection.update_one(
        {"id": movie["id"]},
        {"$set": {"is_watched": movie["is_watched"], "rating": movie["rating"]}},
    )

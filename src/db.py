#jo
import os
from dotenv import load_dotenv
from pymongo import MongoClient

#jo
load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)
collection = client[os.getenv("MONGO_DB")]["movies"]

#mm
DEFAULT_FIELDS = {
    "title": "bez tytułu",
    "genre": "brak",
    "platform": "brak",
    "rating": 0.0,
    "duration": 0,
}

#jo (edit:mm)
def load_movies() -> list:
    return [{**DEFAULT_FIELDS, **movie} for movie in collection.find({}, {"_id": 0})]

#jo
def save_movie(movie: dict) -> None:
    collection.insert_one(dict(movie))

#jo
import os
from dotenv import load_dotenv
from pymongo import MongoClient

#jo
load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)
collection = client[os.getenv("MONGO_DB")]["movies"]

#jo
def load_movies() -> list:
    return list(collection.find({}, {"_id": 0}))

#jo
def save_movie(movie: dict) -> None:
    collection.insert_one(dict(movie))

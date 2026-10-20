#mm
from data import MOVIES
from db import collection

#mm
collection.insert_many(MOVIES)
print("Wysłano filmy do bazy.")

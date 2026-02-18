from fetchers.ilibrary import fetch_ilibrary_db
from fetchers.unglue import fetch_unglue_db
from fetchers.standardebooks import fetch_standardebooks_db
from fetchers import Database
import os

db_exists = os.path.exists("db.json")
db = Database.load("db.json") if db_exists else Database({})

print("Generating db...")

db.books = fetch_ilibrary_db(db.books)
db.books = fetch_unglue_db(db.books)
db.books = fetch_standardebooks_db(db.books)

db.save("db.json")

from fetchers.standardebooks import fetch_standardebooks_db
from fetchers.ilibrary import fetch_ilibrary_db
from fetchers.unglue import fetch_unglue_db
from argparse import ArgumentParser
from fetchers import Database
import os

parser = ArgumentParser()
parser.add_argument("--db", default="db", help="db path")
args = parser.parse_args()

db_exists = os.path.exists(args.db)
db = Database.load(args.db) if db_exists else Database({})

print("Generating db...")

db.books = fetch_ilibrary_db(db.books)

# TODO: accessible only with an account
# db.books = fetch_unglue_db(db.books)

db.books = fetch_standardebooks_db(db.books)

db.save(args.db)

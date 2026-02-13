from fetchers.ilibrary import fetch_ilibrary_db
from fetchers.unglue import fetch_unglue_db

import pickle, os

db = {}

if os.path.exists("db.pickle"):
    with open("db.pickle", "rb") as f:
        db = pickle.load(f)

print("Generating db...")

# db = fetch_ilibrary_db(db)
db = fetch_unglue_db(db)

with open("db.pickle", "wb") as f:
    pickle.dump(db, f, pickle.HIGHEST_PROTOCOL)

from fetchers.ilibrary import fetch_ilibrary_db
from requests.exceptions import InvalidURL
from fetchers.utils import get_soup
import pickle, os

db = {}

if os.path.exists("db.pickle"):
    with open("db.pickle", "rb") as f:
        db = pickle.load(f)

db = fetch_ilibrary_db(db)

with open("db.pickle", "wb") as f:
    pickle.dump(db, f, pickle.HIGHEST_PROTOCOL)

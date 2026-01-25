from fetchers.ilibrary import fetch_ilibrary
from iterfzf import iterfzf
import pickle
import shutil
import sys
import os

if not shutil.which("pandoc"):
    print("Pandoc is required for this :)")
    sys.exit(1)

with open("db.pickle", "rb") as f:
    db = pickle.load(f)

prompt = "(Press Tab for multi-select): "
books = iterfzf(sorted(db.keys()), cycle=True, multi=True, prompt=prompt)

for book in books:
    print(f"Downloading \"{book}\"...")

    meta = db[book]

    # TODO: convert meta to dataclass, meta.source to enum
    if meta["source"] == "ilibrary":
        fetch_ilibrary(meta, f"{book}.epub")
    else:
        raise Exception(f"invalid source: {source}")

from argparse import ArgumentParser
from iterfzf import iterfzf
from fetchers import fetch
import pickle
import shutil
import sys
import os

def main():
    if not shutil.which("pandoc"):
        print("Pandoc is required for this :)")
        sys.exit(1)

    parser = ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Download everything")
    args = parser.parse_args()

    with open("db.pickle", "rb") as f:
        db = pickle.load(f)

    if args.all:
        books = db.keys()
    else:
        prompt = "(Press Tab for multi-select): "
        books = iterfzf(db.keys(), cycle=True, multi=True, prompt=prompt)

    for book in books:
        print(f"Downloading \"{book}\"...")
        fetch(db[book], f"{book}.epub")

    print("Done!")

if __name__ == "__main__":
    main()

from fetchers import fetch, FetchResult
from argparse import ArgumentParser
from iterfzf import iterfzf
from pathlib import Path
import pickle
import shutil
import time
import sys

def main():
    if not shutil.which("pandoc"):
        print("Pandoc is required for this :)")
        sys.exit(1)

    parser = ArgumentParser()
    parser.add_argument("--all", action="store_true", help="Download everything")
    parser.add_argument("-o", "--output", default=".", help="downloads path")
    args = parser.parse_args()

    with open("db.pickle", "rb") as f:
        db = pickle.load(f)

    output_path = Path(args.output)

    books = db.keys()

    if not args.all:
        prompt = "(Press Tab for multi-select): "
        books = iterfzf(books, cycle=True, multi=True, prompt=prompt)

    # skip all downloaded books
    books = [x for x in books if not (output_path / f"{x}.epub").exists()]

    book_count = len(books)

    for i, book in enumerate(books):
        print(f"[{i+1}/{book_count}] Downloading \"{book}\"...")

        fetch_result = fetch(db[book], output_path / f"{book}.epub")
        if fetch_result == FetchResult.NOT_FOUND:
            del db[book]

        time.sleep(3)

    print("Done!")

if __name__ == "__main__":
    main()

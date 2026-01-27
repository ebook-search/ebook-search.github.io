from argparse import ArgumentParser
from utils import hash_long
from iterfzf import iterfzf
from fetchers import fetch
from pathlib import Path
import pickle
import shutil
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

    books = [hash_long(x) for x in books]

    # skip all downloaded books
    books = [x for x in books if not (output_path / f"{x}.epub").exists()]

    book_count = len(books)

    # TODO: for testing github pages
    books = books[:6]

    for i, book in enumerate(books):
        print(f"[{i+1}/{book_count}] Downloading \"{book}\"...")
        fetch(db[book], output_path / f"{book}.epub")

    print("Done!")

if __name__ == "__main__":
    main()

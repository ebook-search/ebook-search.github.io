from fetchers import fetch, FetchResult, Database
from argparse import ArgumentParser
from iterfzf import iterfzf
from pathlib import Path
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

    db = Database.load("db.json")

    output_path = Path(args.output)

    books = db.books.keys()

    if not args.all:
        prompt = "(Press Tab for multi-select): "
        books = iterfzf(books, cycle=True, multi=True, prompt=prompt)

    # skip all downloaded books
    books = [x for x in books if not (output_path / f"{x[:200]}.epub").exists()]

    book_count = len(books)

    for i, book in enumerate(books):
        print(f"[{i+1}/{book_count}] Downloading \"{book}\"...")

        filename = f"{book[:200]}.epub"
        fetch_result = fetch(db.books[book], output_path / filename)
        if fetch_result == FetchResult.NOT_FOUND:
            del db.books[book]

        time.sleep(3)

    db.save("db.json")

    print("Done!")

if __name__ == "__main__":
    main()

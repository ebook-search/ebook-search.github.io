from fetchers import fetch, FetchResult, Database, truncate_filename
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
    parser.add_argument("--db", default="db", help="db path")
    args = parser.parse_args()

    db = Database.load(args.db)

    output_path = Path(args.output)

    books = db.books.keys()

    if not args.all:
        prompt = "(Press Tab for multi-select): "
        books = iterfzf(books, cycle=True, multi=True, prompt=prompt)
    else:
        books = [x for x in books if not (output_path / f"{truncate_filename(x)}.epub").exists()]

        # Github workflow has a limit of 6 hours
        # So let's download 1k books at a time
        books = books[:1000]

    book_count = len(books)

    for i, book in enumerate(books):
        print(f"[{i+1}/{book_count}] Downloading \"{book}\"...")

        filename = f"{truncate_filename(book)}.epub"
        fetch_result = fetch(db.books[book], output_path / filename)
        if fetch_result == FetchResult.NOT_FOUND:
            del db.books[book]

        time.sleep(3)

    db.save("db")

    print("Done!")

if __name__ == "__main__":
    main()

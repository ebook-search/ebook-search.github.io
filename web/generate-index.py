from argparse import ArgumentParser
import pickle
import os

parser = ArgumentParser()
parser.add_argument("-o", "--output", default="index.html", help="index path")
parser.add_argument("--db", default="../db.pickle", help="db path")
args = parser.parse_args()

with open(args.db, "rb") as f:
    db = pickle.load(f)

books = db.keys()

template = lambda books: f"""
<!DOCTYPE html>
<html lang="ru" translate="no">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Книги</title>

		<link rel="stylesheet" href="styles.css">
		<script src="script.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/fzf@0.5.2/dist/fzf.umd.js"></script>
	</head>

    <body class="content">
        <input type="text" id="query" placeholder="Поиск..." autocomplete="off">
        <ul id="books">{books}</ul>
    </body>
</html>
"""

book_elements = [
    f'<li class="book"><a href="./d/{name}.epub">{name}</a></li>'
    for name in books
]

index = template("".join(book_elements))
with open(args.output, "w") as f:
    f.write(index)

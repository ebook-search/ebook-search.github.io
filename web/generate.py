from utils import hash_long
import pickle
import os

with open("db.pickle", "rb") as f:
    db = pickle.load(f)

books = [hash_long(x) for x in db.keys()]

template = lambda books: f"""
<!DOCTYPE html>
<html lang="ru" translate="no">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>Книги</title>

		<link rel="stylesheet" href="styles.css">
		<script src="script.js"></script>
	</head>

    <body class="content">
        <input type="text" id="query" placeholder="Поиск..." autocomplete="off">
        <ul id="books">{books}</ul>
    </body>
</html>
"""

book_elements = [
    f'<li class="book"><a href="./data/{name}.epub">{name}</a></li>'
    for name in books
]

index = template("".join(book_elements))
with open("index.html", "w") as f:
    f.write(index)

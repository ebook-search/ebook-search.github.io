import pickle
import os

os.makedirs("data", exist_ok=True)

# TODO: move all epubs from ../ to data

with open("../db.pickle", "rb") as f:
    db = pickle.load(f)

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

	<body>
		<input type="text" id="query" placeholder="Поиск..." autocomplete="off">

		<ul id="books">{books}</ul>
	</body>
</html>
"""

# <li class="book"><a href="./test2">А. Достоевский - Тестбук1</a></li>
# <li class="book"><a href="./test">А. Петров - Тестобуко9</a></li>

books = [
    f'<li class="book"><a href="./UNKNOWNYETSORRY">{name}</a></li>'
    for name in db.keys()
]
books = "".join(books)

index = template(books)
with open("index.html", "w") as f:
    f.write(index)

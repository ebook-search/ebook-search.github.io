import shutil
import os

os.makedirs("data", exist_ok=True)

books = [x.removesuffix(".epub") for x in os.listdir("..") if x.endswith(".epub")]

for book in books:
    shutil.move(f"../{book}.epub", f"data/{book}.epub")

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

book_elements = [
    f'<li class="book"><a href="./data/{name}.epub">{name}</a></li>'
    for name in books
]

index = template("".join(book_elements))
with open("index.html", "w") as f:
    f.write(index)

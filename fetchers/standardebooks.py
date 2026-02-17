from . import get_soup, Meta, MetaSource, FetchResult
from urllib.request import urlretrieve
from urllib.error import HTTPError

SE_BASE_URL = "https://standardebooks.org"

def _parse_book_entry(item):
    link = item.find("p").find("a")
    title = link.find("span", property="schema:name").text
    url = link.attrs["href"]

    authors = []
    for author_p in item.find_all("p", class_="author"):
        author_link = author_p.find("a")
        if author_link:
            author_name = author_link.find("span", property="schema:name").text
            authors.append(author_name)

    return {
        "title": title,
        "authors": authors,
        "url": url,
    }

def _fetch_page_books(page_url):
    soup = get_soup(page_url)
    items = soup.select("li[typeof='schema:Book']")
    books = [_parse_book_entry(item) for item in items]
    return books

def fetch_standardebooks_db(db):
    page = 1

    while True:
        url = f"{SE_BASE_URL}/ebooks?page={page}&per-page=48"
        books = _fetch_page_books(url)

        if len(books) == 0:
            break

        for book in books:
            url_path = book["url"]
            meta = Meta(
                authors=book["authors"],
                title=book["title"],
                language="en",
                source=MetaSource.STANDARDEBOOKS,
                data={"url": url_path},
            )
            db[meta.entry] = meta

        if len(books) < 48:
            break

        page += 1

    return db

def fetch_standardebooks(meta, output_path):
    url_path = meta.data["url"]

    slug = url_path.replace("/ebooks/", "").replace("/", "_")
    epub_url = f"{SE_BASE_URL}{url_path}/downloads/{slug}.epub?source=feed"

    try:
        urlretrieve(epub_url, output_path)
    except HTTPError:
        return FetchResult.NOT_FOUND

    return FetchResult.SUCCESS

from fetchers import Database, MetaSource
from collections import defaultdict
from xml.sax.saxutils import escape
from datetime import datetime
import os


ATOM_NS = "http://www.w3.org/2005/Atom"
OPDS_NS = "http://opds-spec.org/2010/catalog"
CATALOG_MEDIA_TYPE = "application/atom+xml;profile=opds-catalog"
EPUB_MEDIA_TYPE = "application/epub+zip"
ACQUISITION_REL = "http://opds-spec.org/acquisition"

def group_books_by_author(db):
    books_by_author = defaultdict(list)
    for title, meta in db.books.items():
        for author in meta.authors:
            books_by_author[author].append((title, meta))
    return books_by_author

def group_books_by_source(db):
    books_by_source = defaultdict(list)
    for title, meta in db.books.items():
        books_by_source[meta.source].append((title, meta))
    return books_by_source

def slugify(text):
    return text.replace("/", "-").replace(" ", "_")

def make_nav_feed(groups, section_type):
    links = []
    for name in sorted(groups.keys()):
        slug = slugify(name)
        if section_type == "author":
            href = f"author/{slug}.xml"
        else:
            href = f"source/{slug.lower()}.xml"
        links.append(
            f'  <link '
            f'href="{href}" '
            f'title="{escape(name)}" '
            f'type="{CATALOG_MEDIA_TYPE}" '
            f'rel="subsection"/>'
        )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="{ATOM_NS}" xmlns:opds="{OPDS_NS}">
  <title>Книги</title>
  <id>urn:ebook-search:nav</id>
  <updated>{datetime.now().isoformat()}Z</updated>
  <link rel="start" href="index.xml" type="{CATALOG_MEDIA_TYPE}"/>
{chr(10).join(links)}
</feed>"""


def make_book_entry(title, author, filename, timestamp):
    return f"""  <entry>
    <title>{escape(title)}</title>
    <id>urn:ebook-search:book:{escape(title)}</id>
    <updated>{timestamp}</updated>
    <link href="../../d/{escape(filename)}" type="{EPUB_MEDIA_TYPE}" rel="{ACQUISITION_REL}"/>
    <author>
      <name>{escape(author)}</name>
    </author>
  </entry>"""


def make_author_feed(author, books):
    timestamp = datetime.now().isoformat() + "Z"
    slug = slugify(author)

    entries = []
    for title, _ in sorted(books, key=lambda x: x[0]):
        filename = f"{title}.epub"
        entries.append(make_book_entry(title, author, filename, timestamp))

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="{ATOM_NS}" xmlns:opds="{OPDS_NS}">
  <title>{escape(author)}</title>
  <id>urn:ebook-search:author:{escape(author)}</id>
  <updated>{timestamp}</updated>
  <link rel="start" href="../index.xml" type="{CATALOG_MEDIA_TYPE}"/>
  <link rel="up" href="../index.xml" type="{CATALOG_MEDIA_TYPE}"/>
{chr(10).join(entries)}
</feed>"""

def make_source_feed(source, books):
    timestamp = datetime.now().isoformat() + "Z"
    slug = source.name.lower()

    entries = []
    for title, meta in sorted(books, key=lambda x: x[0]):
        filename = f"{title}.epub"
        author = ", ".join(meta.authors) if meta.authors else "Unknown"
        entries.append(make_book_entry(title, author, filename, timestamp))

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="{ATOM_NS}" xmlns:opds="{OPDS_NS}">
  <title>{source.value}</title>
  <id>urn:ebook-search:source:{source.value}</id>
  <updated>{timestamp}</updated>
  <link rel="start" href="../index.xml" type="{CATALOG_MEDIA_TYPE}"/>
  <link rel="up" href="../index.xml" type="{CATALOG_MEDIA_TYPE}"/>
{chr(10).join(entries)}
</feed>"""

db = Database.load("web/db.json")

books_by_author = group_books_by_author(db)
books_by_source = group_books_by_source(db)

os.makedirs("web/opds/author", exist_ok=True)
os.makedirs("web/opds/source", exist_ok=True)

nav_feed = make_nav_feed(books_by_author, "author")
with open("web/opds/index.xml", "w", encoding="utf-8") as f:
    f.write(nav_feed)

for author, books in books_by_author.items():
    author_feed = make_author_feed(author, books)
    slug = slugify(author)
    with open(f"web/opds/author/{slug}.xml", "w", encoding="utf-8") as f:
        f.write(author_feed)

for source, books in books_by_source.items():
    source_feed = make_source_feed(source, books)
    slug = source.name.lower()
    with open(f"web/opds/source/{slug}.xml", "w", encoding="utf-8") as f:
        f.write(source_feed)

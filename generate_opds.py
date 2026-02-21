from fetchers import Database, MetaSource, truncate_filename
from argparse import ArgumentParser
from collections import defaultdict
from xml.etree import ElementTree as ET
from datetime import datetime
import logging
from pathlib import Path

ATOM_NS = "http://www.w3.org/2005/Atom"
OPDS_NS = "http://opds-spec.org/2010/catalog"
CATALOG_MEDIA_TYPE = "application/atom+xml;profile=opds-catalog"
EPUB_MEDIA_TYPE = "application/epub+zip"
ACQUISITION_REL = "http://opds-spec.org/acquisition"

ET.register_namespace("", ATOM_NS)
ET.register_namespace("opds", OPDS_NS)

parser = ArgumentParser()
parser.add_argument("-o", "--output", default="web/opds", help="output directory path")
parser.add_argument("--db", default="db", help="database path")
args = parser.parse_args()

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

def create_feed_element(title, feed_id):
    feed = ET.Element("feed", xmlns=ATOM_NS)
    feed.set(f"{{{OPDS_NS}}}catalog", "yes")

    title_elem = ET.SubElement(feed, "title")
    title_elem.text = title

    id_elem = ET.SubElement(feed, "id")
    id_elem.text = feed_id

    updated_elem = ET.SubElement(feed, "updated")
    updated_elem.text = datetime.now().isoformat() + "Z"

    return feed

def add_book_entry(feed, title, author, filename):
    entry = ET.SubElement(feed, "entry")

    title_elem = ET.SubElement(entry, "title")
    title_elem.text = title

    id_elem = ET.SubElement(entry, "id")
    id_elem.text = f"urn:ebook-search:book:{title}"

    updated_elem = ET.SubElement(entry, "updated")
    updated_elem.text = datetime.now().isoformat() + "Z"

    link = ET.SubElement(entry, "link", href=f"../d/{filename}", type=EPUB_MEDIA_TYPE, rel=ACQUISITION_REL)

    author_elem = ET.SubElement(entry, "author")
    author_name = ET.SubElement(author_elem, "name")
    author_name.text = author

def feed_to_xml_string(feed):
    xml_str = ET.tostring(feed, encoding="unicode")
    return f'<?xml version="1.0" encoding="UTF-8"?>\n{xml_str}'

def generate_author_feeds(output_dir, books_by_author):
    author_dir = Path(output_dir) / "author"

    shutil.rmtree(author_dir)
    author_dir.mkdir(parents=True, exist_ok=True)

    for author, books in books_by_author.items():
        feed = create_feed_element(author, f"urn:ebook-search:author:{author}")

        ET.SubElement(feed, "link", rel="start", href="../index.xml", type=CATALOG_MEDIA_TYPE)
        ET.SubElement(feed, "link", rel="up", href="../index.xml", type=CATALOG_MEDIA_TYPE)

        for title, meta in sorted(books, key=lambda x: x[0]):
            filename = truncate_filename(f"{title}.epub")
            add_book_entry(feed, title, author, filename)

        slug = slugify(author)
        output_file = author_dir / f"{slug}.xml"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(feed_to_xml_string(feed))

        print(f"Generated author feed: {output_file}")

def generate_source_feeds(output_dir, books_by_source):
    source_dir = Path(output_dir) / "source"

    shutil.rmtree(source_dir)
    source_dir.mkdir(parents=True, exist_ok=True)

    for source, books in books_by_source.items():
        feed = create_feed_element(source.value, f"urn:ebook-search:source:{source.value}")

        ET.SubElement(feed, "link", rel="start", href="../index.xml", type=CATALOG_MEDIA_TYPE)
        ET.SubElement(feed, "link", rel="up", href="../index.xml", type=CATALOG_MEDIA_TYPE)

        for title, meta in sorted(books, key=lambda x: x[0]):
            filename = truncate_filename(f"{title}.epub")
            author = ", ".join(meta.authors) if meta.authors else "Unknown"
            add_book_entry(feed, title, author, filename)

        slug = slugify(source.name)
        output_file = source_dir / f"{slug}.xml"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(feed_to_xml_string(feed))

        print(f"Generated source feed: {output_file}")

def generate_nav_feed(output_file, groups, section_type):
    feed = create_feed_element("Книги", "urn:ebook-search:nav")

    ET.SubElement(feed, "link", rel="start", href="index.xml", type=CATALOG_MEDIA_TYPE)

    for name in sorted(groups.keys()):
        slug = slugify(name)
        href = f"{section_type}/{slug}.xml"
        ET.SubElement(feed, "link", href=href, title=name, type=CATALOG_MEDIA_TYPE, rel="subsection")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(feed_to_xml_string(feed))

    print(f"Generated navigation feed: {output_file}")

db = Database.load(args.db)
print(f"Loaded database from {args.db} ({len(db.books)} books)")

books_by_author = group_books_by_author(db)
books_by_source = group_books_by_source(db)

output_dir = Path(args.output)
output_dir.mkdir(parents=True, exist_ok=True)

generate_nav_feed(output_dir / "index.xml", books_by_author, "author")
generate_author_feeds(output_dir, books_by_author)
generate_source_feeds(output_dir, books_by_source)

print(f"OPDS generation complete: {len(books_by_author)} authors, {len(books_by_source)} sources")

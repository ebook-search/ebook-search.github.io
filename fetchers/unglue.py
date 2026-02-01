from fetchers.utils import Meta, MetaSource
from urllib.request import urlretrieve
from pymarc import parse_xml_to_array
from io import BytesIO
import requests
import re

def fetch_unglue_db(db):
    params = {"format": "xml", "link_target": "direct", "submit": "Download+All+Records"}
    marc = BytesIO(requests.post("https://unglue.it/marc/all", params=params).content)

    records = parse_xml_to_array(marc)

    for record in records:
        title = record.title.removesuffix(" /")

        author = record.author

        editor = record.get("700")
        if editor:
            editor = editor.format_field()

        author = author or editor

        if author:
            # "Luther, Martin, author." -> "Luther, Martin, author"
            author = author.removesuffix(".")

            # "Luther, Martin,  author" -> ["Luther", "Martin", "author"]
            author_parts = [x.strip() for x in author.split(", ")]

            # ["Luther", "Martin", "author"] -> ["Luther", "Martin"]
            if author_parts[-1] in ["author", "editor"]:
                author_parts.pop()

            # ["Luther", "Martin"] -> "Martin Luther"
            author = " ".join(author_parts[::-1])
        else:
            author = "(Неизвестен)"

        epub_url = None
        mobi_url = None
        for field in record.fields:
            if field.tag != "856": continue

            value = field.value()
            (file_format, _, _, _url) = value.split(" ")

            if file_format == "epub":
                epub_url = _url
            elif file_format == "mobi":
                mobi_url = _url

        url = epub_url or mobi_url
        if url == None: continue

        meta = Meta(
            authors = [author],
            title = title,
            source = MetaSource.UNGLUE,
            data = {"url": url},
        )
        db[meta.entry] = meta

    return db

def fetch_unglue(meta, output_path):
    url = meta.data["url"]
    urlretrieve(url, output_path)

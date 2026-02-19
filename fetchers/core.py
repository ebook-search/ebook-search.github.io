from dataclasses import dataclass
from bs4 import BeautifulSoup
from retrying import retry
from enum import Enum
import subprocess
import requests
import json
import os

class MetaSource(Enum):
    ILIBRARY = "ilibrary"
    UNGLUE = "unglue"
    STANDARDEBOOKS = "standardebooks"

class FetchResult(Enum):
    SUCCESS = 1
    NOT_FOUND = 2

@dataclass
class Meta():
    authors: list[str]
    title: str
    language: str | None
    source: MetaSource
    data: dict

    @property
    def entry(self):
        authors = ", ".join(self.authors)
        if authors == "": authors = "(Автор неизвестен)"

        title = self.title[:150]

        return f"{authors} - {title}"

    def to_dict(self):
        d = self.__dict__.copy()
        d["source"] = d["source"].name
        return d

    @classmethod
    def from_dict(cls, data):
        data = data.copy()
        data["source"] = MetaSource[data["source"]]
        return cls(**data)

@dataclass
class Database():
    books: dict[str, Meta]

    def save(self, path):
        full_db = os.path.join(path, "full.json")
        slugs_db = os.path.join(path, "slugs.json")

        if os.path.exists(path):
            [os.remove(file) for file in (full_db, slugs_db)]
            os.rmdir(path)

        with open(full_db, "w") as f:
            json.dump({k: v.to_dict() for k, v in self.books.items()}, f)

        with open(slugs_db, "w") as f:
            slugs = list(self.books.keys())
            slugs = [truncate_filename(x) for x in slugs]
            json.dump(slugs, f)

    @classmethod
    def load(cls, path):
        full_db = os.path.join(path, "full.json")

        with open(full_db, "r") as f:
            data = json.load(f)

        return cls({k: Meta.from_dict(v) for k, v in data.items()})

@retry(stop_max_attempt_number=5)
def get_soup(url):
    headers = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36" }
    page_content = requests.get(url, headers=headers).text
    return BeautifulSoup(page_content, features="html.parser")

def make_book(meta, pages, output_path):
    title = meta.title
    authors = ", ".join(meta.authors)

    cmd = ["pandoc"]

    cmd.extend([
        f"--metadata=title:{title}",
        f"--metadata=author:{authors}",
    ])

    if meta.language:
        cmd.append(f"--metadata=lang:{meta.language}")

    cmd.extend([
        "--epub-title-page=false",

        "-o", output_path,
        *pages,
    ])

    return subprocess.run(cmd)

def truncate_filename(x, max_bytes=240):
    encoded = x.encode("utf-8")
    if len(encoded) <= max_bytes: return x
    return encoded[:max_bytes].decode("utf-8", errors="ignore")

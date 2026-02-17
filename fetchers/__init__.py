from dataclasses import dataclass
from bs4 import BeautifulSoup
from retrying import retry
from enum import Enum
import subprocess
import requests

def fetch(meta, output_path):
    table = {
        MetaSource.ILIBRARY: fetch_ilibrary,
        MetaSource.UNGLUE:   fetch_unglue,
    }

    source = meta.source
    return table[source](meta, output_path)

class MetaSource(Enum):
    ILIBRARY = 1
    UNGLUE = 2

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

def normalize(text):
    table = {
        "\N{EM DASH}": "-",
    }

    for key, value in table.items():
        text = text.replace(key, value)

    return text

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

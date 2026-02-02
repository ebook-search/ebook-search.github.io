from dataclasses import dataclass
from bs4 import BeautifulSoup
from enum import Enum
import subprocess
import requests

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

def get_soup(url):
    page_content = requests.get(url).text
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

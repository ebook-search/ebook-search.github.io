from bs4 import BeautifulSoup
import subprocess
import requests

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
    title = meta["title"]
    authors = ", ".join(meta["authors"])

    return subprocess.run([
        "pandoc",

        f"--metadata=title:{title}",
        f"--metadata=author:{authors}",
        "--metadata=lang:ru",

        "--epub-title-page=false",

        "-o", output_path,
        *pages,
    ])

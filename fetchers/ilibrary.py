from fetchers.utils import get_soup, normalize, make_book
from tempfile import TemporaryDirectory
import os

def _get_ilibrary_link(work_id, page_id):
    return f"https://ilibrary.ru/text/{work_id}/p.{page_id}/index.html"

def fetch_ilibrary_meta(work_id):
    url = _get_ilibrary_link(work_id, 1)

    soup = get_soup(url)

    data = soup.find("div", id="thdr").find_all("a")

    author_title_block = [x.text for x in data]
    title = author_title_block.pop()
    authors = author_title_block

    content = soup.find("div", id="text")

    toc = content.find("span", id="toc")
    page_count = int(toc.text.split("/")[1]) if toc else 1

    return {
        "authors": authors,
        "title": title,
        "page_count": page_count,
        "source": "ilibrary",
        "data": {"id": work_id},
    }

def fetch_ilibrary_page(work_id, page_id):
    url = _get_ilibrary_link(work_id, page_id)

    lines = []

    soup = get_soup(url)
    content = soup.find("div", id="text")

    for x in content.find_all(["iframe", "script"]):
        x.decompose()

    # Empty tags
    for x in content.find_all(["o", "c", "m"]):
        if x.text != "": raise Exception("not empty!")
        x.decompose()

    # One line author(s) + name
    content.find("div", id="thdr").decompose()

    # Empty tag
    content.find("div", id="tbd").decompose()

    for z in content.find_all("z"):
        z.name = "p"

    # Empty
    bnbg = content.find("div", id="bnbg")
    if bnbg: bnbg.parent.decompose()

    author = content.find("div", class_="author")
    if author: author.decompose()

    title = content.find("div", class_="title")
    if title: title.decompose()

    if len(content.find_all("h1")) > 0:
        raise Exception("WHAAT :O")

    # Offset all headings
    for h in content.find_all(["h2", "h3", "h4", "h5", "h6"]):
        h.name = f"h{int(h.name.removeprefix('h')) - 1}"

    # Poetry: wrappers
    for x in content.find_all(["pmm", "pms", "pm"]):
        x.unwrap()

    # Poetry: wrapper
    for pmt in content.select('div[id^="pmt"]'):
        pmt.unwrap()

    # Poetry: lines
    for v in content.find_all("v"):
        v.insert_after(soup.new_tag("br"))
        v.unwrap()

    # Poetry: dot breaks
    for br in content.find_all("span", class_="dots d1"):
        br.replace_with(soup.new_tag("p"))

    # Labels? (found in "Повесть временных лет")
    for x in content.find_all("span", class_="label"):
        x.decompose()

    for x in content.find_all("div", class_="letter_formaddress"):
        x.unwrap()

    # Page end decoration
    page_end_dec = content.find("div", class_="i0 tc")
    if page_end_dec: page_end_dec.decompose()

    # TODO: styles:
    # letter_presignature {
    #     text-align: right;
    #     margin: 0 20;
    # }

    return normalize("".join(str(child) for child in content.contents))

    # for block in content.find_all(["z", "h1", "h2", "h3"]):
    #     for note in block.find_all("fn"):
    #         note_id = note.find("a").get("id", "").removeprefix("fnr")
    #         note.replace_with(f"[^{note_id}]")
    #
    # footnotes = content.find("div", class_="fns") or []
    # for note in footnotes:
    #     note_id = note.attrs["id"].removeprefix("fnt")
    #     note = " ".join([x.text for x in note.find_all("z", recursive=False)])
    #     lines.append(f"[^{note_id}]: {note}")
    #
    # return "\n".join(lines)

def fetch_ilibrary(meta, output_path):
    work_id = meta["data"]["id"]

    page_count = meta["page_count"]

    with TemporaryDirectory() as tmp:
        pages = []
        for page_index in range(page_count):
            page_id = page_index + 1
            page = fetch_ilibrary_page(work_id, page_id)

            path = os.path.join(tmp, f"{page_id}.html")

            with open(path, "w") as f:
                f.write(page)

            pages.append(path)

        make_book(meta, pages, output_path)

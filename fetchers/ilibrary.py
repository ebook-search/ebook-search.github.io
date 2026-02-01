from fetchers.utils import get_soup, normalize, make_book, Meta, MetaSource
from tempfile import TemporaryDirectory
import os

def _get_ilibrary_link(work_id, page_id):
    return f"https://ilibrary.ru/text/{work_id}/p.{page_id}/index.html"

def _fetch_ilibrary_meta(work_id):
    url = _get_ilibrary_link(work_id, 1)
    soup = get_soup(url)

    data = soup.find("div", id="thdr").find_all("a")

    author_title_block = [x.text for x in data]
    title = author_title_block.pop()
    authors = author_title_block

    content = soup.find("div", id="text")

    toc = content.find("span", id="toc")
    page_count = int(toc.text.split("/")[1]) if toc else 1

    return Meta(
        authors = [authors],
        title = title,
        source = MetaSource.ILIBRARY,
        data = {"id": work_id, "page_count": page_count},
    )

def fetch_ilibrary_db(db):
    ilibrary_entries = [x for x in db.values() if x.source == MetaSource.ILIBRARY]
    ilibrary_ids = [x.data["id"] for x in ilibrary_entries]
    ilibrary_last_id = max([0, *ilibrary_ids])

    soup = get_soup("https://ilibrary.ru")

    latest = soup.find("div", id="ltstin").find("ul", class_="ltst_l").find("li").a
    latest_id = int(latest.attrs["href"].split("/")[2])

    for i in range(ilibrary_last_id, latest_id):
        current_work = i + 1

        try:
            meta = _fetch_ilibrary_meta(current_work)
            db[meta.entry] = meta

            print(f"[ilibrary]: {current_work}")
        except InvalidURL:
            continue

    return db

def _fetch_ilibrary_page(work_id, page_id):
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
    tbd = content.find("div", id="tbd")
    if tbd:
        tbd.decompose()

    for z in content.find_all("z"):
        z.name = "p"

    # Empty
    bnbg = content.find("div", id="bnbg")
    if bnbg: bnbg.parent.decompose()

    author = content.find("div", class_="author")
    if author: author.decompose()

    title = content.find("div", class_="title")
    if title: title.decompose()

    # Unknown hidden element (found in "Кому на руси жить хорошо")
    for eh in content.find_all("eh"):
        eh.decompose()

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

    # Remove all inline styling
    for x in content.select("[style]"):
        x.attrs.pop("style")

    # TODO: fix
    # Повести покойного Ивана Петровича Белкина: epigraphs

    # TODO: styles:
    # letter_presignature {
    #     text-align: right;
    #     margin: 0 20;
    # }

    return normalize("".join(str(child) for child in content.contents))

# TODO: can be "generalized"
def fetch_ilibrary(meta, output_path):
    with TemporaryDirectory() as tmp:
        pages = []

        for page_index in range(meta.data["page_count"]):
            page_id = page_index + 1
            page = _fetch_ilibrary_page(meta.data["id"], page_id)

            path = os.path.join(tmp, f"{page_id}.html")

            with open(path, "w") as f:
                f.write(page)

            pages.append(path)

        make_book(meta, pages, output_path)

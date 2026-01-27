from fetchers.ilibrary import fetch_ilibrary_meta
from requests.exceptions import InvalidURL
from fetchers.utils import get_soup
import pickle, os

db = {}

ilibrary_last_id = 0

if os.path.exists("db.pickle"):
    with open("db.pickle", "rb") as f:
        db = pickle.load(f)
    ilibrary_last_id = max([x["data"]["id"] for x in db.values() if x["source"] == "ilibrary"])

soup = get_soup("https://ilibrary.ru")

latest = soup.find("div", id="ltstin").find("ul", class_="ltst_l").find("li").a
latest_id = int(latest.attrs["href"].split("/")[2])

for i in range(ilibrary_last_id, latest_id):
    current_work = i + 1

    try:
        meta = fetch_ilibrary_meta(current_work)

        authors = ", ".join(meta["authors"])
        if authors == "": authors = "(Автор неизвестен)"

        title = meta["title"]
        if len(title) > 150: title = title[:150]

        entry = f"{authors} - {title}"
        db[entry] = meta

        print(f"[ilibrary]: {current_work}")
    except InvalidURL:
        continue

    current_work += 1

    # TODO: for testing github pages
    if current_work > 10: break

with open("db.pickle", "wb") as f:
    pickle.dump(db, f, pickle.HIGHEST_PROTOCOL)

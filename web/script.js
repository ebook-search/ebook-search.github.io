const params = new URLSearchParams(window.location.search);
const query = params.get("q") || "";

const searchResultsScreen = query.length > 0;

// If on main page, prefetch the db in background to speed up searches
if (!searchResultsScreen) { _getRawDB(); }

function truncateFilename(s, maxBytes = 240) {
    const encoded = new TextEncoder().encode(s);
    if (encoded.length <= maxBytes) return s;
    return new TextDecoder("utf-8", { errors: "ignore" }).decode(encoded.slice(0, maxBytes));
}

function display(elem, value) {
    elem.style.display = value ? "revert-layer" : "none";
}

async function getFileContents(url_path) {
    const host = window.location.host;
    const protocol = window.location.protocol;
    const url = `${protocol}//${host}/${url_path}`;

	const response = await fetch(url);
	return await response.text();
}

async function _getRawDB() {
    const cached = sessionStorage.getItem("db");
    if (cached) { return cached; }

    const raw = await getFileContents("db.json");
    sessionStorage.setItem("db", raw);
    return raw;
}

async function getDB() {
    const db = await _getRawDB();
    return JSON.parse(db);
}

async function search(query) {
    const db = await getDB();

    const fzf = new window.fzf.AsyncFzf(Object.entries(db), {
      selector: (x) => x[0],
    });

    const books = await fzf.find(query);

    const booksList = document.getElementById("books");

    booksList.innerHTML = books.map((book) => {
        const [name] = book.item;
        return `<li class="book"><a href="./d/${encodeURI(truncateFilename(name))}.epub">${name}</a></li>`;
    }).join("");
}

document.addEventListener("DOMContentLoaded", function() {
    let elems = document.querySelectorAll("input#query");
    for (let elem of elems) { elem.value = query; }

    const screen = (searchResultsScreen) ? "form#results" : "form#search";
    display(document.querySelector(screen), true);

    if (searchResultsScreen) { search(query); }
})

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

async function fetchDB() {
    const cached = sessionStorage.getItem("db");
    if (cached) {
        return JSON.parse(cached);
    }

    const raw = await getFileContents("db.json");
    sessionStorage.setItem("db", raw);

    return JSON.parse(raw);
}

async function search(query) {
    const db = await fetchDB();

    const fzf = new window.fzf.AsyncFzf(Object.entries(db), {
      selector: (x) => x[0],
    });

    const books = await fzf.find(query);

    const booksList = document.getElementById("books");

    for (const book of books) {
        const [name, data] = book.item;

        const li = document.createElement("li");
        li.className = "book";

        const a = document.createElement("a");
        // TODO: strip name to 200 chars
        a.href = `./d/${encodeURI(name)}.epub`;
        a.textContent = name;

        li.appendChild(a);
        booksList.appendChild(li);
    }
}

document.addEventListener("DOMContentLoaded", function() {
    const params = new URLSearchParams(window.location.search);
    const query = params.get("q") || "";

    let elems = document.querySelectorAll("input#query");
    for (let elem of elems) {
        elem.value = query;
    }

    let screen;

    const showSearchResults = query.length > 0;

    if (showSearchResults) {
        screen = "form#results";
        search(query);
    } else {
        screen = "form#search";
    }

    requestAnimationFrame(() => {
        display(document.querySelector(screen), true);
    });
})

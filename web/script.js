function search() {
    const raw_query = document.getElementById("query").value;
    const query = raw_query.toLowerCase().trim();

    const empty_query = query.length == 0;

    const books = document.querySelectorAll("ul#books li");
    for (book of books) {
        const book_name = book.innerHTML.toLowerCase();

        const match = book_name.includes(query) || empty_query;
        book.style.display = match ? "" : "none";
    }
}

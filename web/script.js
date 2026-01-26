document.addEventListener("DOMContentLoaded", function() {
    const books = Array.from(document.querySelectorAll("ul#books li"));

    function search() {
        const raw_query = document.getElementById("query").value;
        const query = raw_query.toLowerCase().trim();
        const empty_query = query.length === 0;

        requestAnimationFrame(() => {
            for (let book of books) {
                const book_name = book.textContent.toLowerCase();
                const match = book_name.includes(query) || empty_query;
                book.style.display = match ? "" : "none";
            }
        })
    }

    const query = document.getElementById("query");
    query.addEventListener("input", search);
})

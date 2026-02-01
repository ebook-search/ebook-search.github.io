document.addEventListener("DOMContentLoaded", function() {
    const FzF = window.fzf.Fzf;

    const books = Array.from(document.querySelectorAll("ul#books li a"));

    const fzf = new FzF(books, {
      selector: (item) => item.textContent,
    });

    function search() {
        const raw_query = document.getElementById("query").value;
        const results = fzf.find(raw_query);

        requestAnimationFrame(() => {
            for (let book of books) {
                book.style.display = "none";
            }

            for (let result of results) {
                result.item.style.display = "";
            }
        })
    }

    const search_bar = document.getElementById("query");
    search_bar.addEventListener("input", search);
})

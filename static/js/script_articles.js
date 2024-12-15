document.addEventListener("DOMContentLoaded", () => {
    const articlesContainer = document.getElementById("articles-container");

    // Fetch articles from Flask backend
    fetch("http://127.0.0.1:5000/get_articles")
        .then((response) => response.json())
        .then((articles) => {
            if (articles.error) {
                articlesContainer.innerHTML = `<p>${articles.error}</p>`;
                return;
            }

            // Populate articles
            articles.forEach((article) => {
                const articleElement = document.createElement("div");
                articleElement.classList.add("article");
                articleElement.innerHTML = `
                    <h2>${article.title}</h2>
                    <p>${article.description || "No description available."}</p>
                    <a href="${article.url}" target="_blank">Read more at ${article.source}</a>
                `;
                articlesContainer.appendChild(articleElement);
            });
        })
        .catch((error) => {
            console.error("Error fetching articles:", error);
            articlesContainer.innerHTML = `<p>Failed to load articles. Please try again later.</p>`;
        });

    // Redirect to home
    document.getElementById("homeBtn").addEventListener("click", () => {
        window.location.href = "/dashboard";
    });
});

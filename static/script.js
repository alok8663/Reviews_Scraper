document.addEventListener("DOMContentLoaded", function () {
    const urlInput = document.getElementById("product-url");

    urlInput.addEventListener("paste", function () {
        setTimeout(() => {
            const value = urlInput.value.trim();
            if (value.startsWith("http://") || value.startsWith("https://")) {
                urlInput.classList.add("link-pasted");
            } else {
                urlInput.classList.remove("link-pasted");
            }
        }, 100);
    });

    urlInput.addEventListener("input", function () {
        if (!urlInput.value.trim()) {
            urlInput.classList.remove("link-pasted");
        }
    });
});

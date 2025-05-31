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


function pollProgress() {
    document.getElementById("progress-container").style.display = "block";
    const interval = setInterval(() => {
        fetch('/progress')
            .then(res => res.json())
            .then(data => {
                const value = data.value;
                document.getElementById("bar").style.width = value + "%";
                document.getElementById("percent").innerText = value + "%";
                if (value >= 100) clearInterval(interval);
            });
    }, 1000);
}


from flask import Flask, render_template, request, send_file
import os
import re
from amazon_scraper import scrape_amazon_reviews
from flipkart_scraper import scrape_flipkart_reviews

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    file_to_download = None

    if request.method == 'POST':
        url = request.form.get('product_url')
        platform = request.form.get('platform')
        pages = int(request.form.get('pages', 1))

        if not url:
            return render_template("index.html", error="⚠️ Please enter a valid product URL.")

        if platform == 'amazon':
            try:
                asin_match = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
                if not asin_match:
                    return render_template("index.html", error="❌ Invalid Amazon product URL.")
                asin = asin_match.group(1)
                user_id = request.remote_addr.replace(".", "_")
                scrape_amazon_reviews(asin, pages, user_id)
                message = "✅ Amazon scraping completed!"
                file_to_download = "amazon_reviews.json"
            except Exception as e:
                message = f"❌ Amazon scraping failed: {str(e)}"

        elif platform == 'flipkart':
            try:
                if "flipkart.com" not in url:
                    return render_template("index.html", error="❌ Invalid Flipkart product URL.")
                scrape_flipkart_reviews(url)
                message = "✅ Flipkart scraping completed!"
                file_to_download = "flipkart_reviews.json"
            except Exception as e:
                message = f"❌ Flipkart scraping failed: {str(e)}"

    return render_template("index.html", message=message, file=file_to_download)


@app.route('/download/<platform>')
def download(platform):
    if platform == "amazon":
        path = os.path.join(BASE_DIR, "amazon_reviews.json")
    elif platform == "flipkart":
        path = os.path.join(BASE_DIR, "flipkart_reviews.json")
    else:
        return "Invalid platform", 400

    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    else:
        return "File not found", 404


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, send_file
import os
import re
from amazon_scraper import scrape_amazon_reviews
from flipkart_scraper import scrape_flipkart_reviews
import json


progress_data = {"value": 0}

def update_progress(current, total):
    progress_data["value"] = int((current / total) * 100)



app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    error = None
    file_to_download = None

    if request.method == 'POST':
        url = request.form.get('product_url')
        platform = request.form.get('platform')
        pages = int(request.form.get('pages', 1))

        if not url:
            return render_template("index.html", error="⚠️ Please enter a valid product URL.")

        try:
            if platform == 'amazon':
                asin_match = re.search(r"/([A-Z0-9]{10})(?:[/?]|$)", url)
                if not asin_match:
                    return render_template("index.html", error="❌ Invalid Amazon product URL.")
                asin = asin_match.group(1)
                user_id = request.remote_addr.replace(".", "_")
                scrape_amazon_reviews(asin, pages, user_id, progress_callback=update_progress)
                filename = "amazon_reviews.json"

            elif platform == 'flipkart':
                try:
                    if "flipkart.com" not in url:
                        return render_template("index.html", error="❌ Invalid Flipkart product URL.")

                    filename = "flipkart_reviews.json"
                    filepath = os.path.join(BASE_DIR, filename)

                    # ✅ Delete old file before scraping
                    if os.path.exists(filepath):
                        os.remove(filepath)

                    scrape_flipkart_reviews(url, progress_callback=update_progress)


                    if os.path.exists(filepath):
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = f.read().strip()
                            reviews = json.loads(data)
                            if isinstance(reviews, list) and len(reviews) > 0:
                                message = "✅ Flipkart scraping completed!"
                                file_to_download = filename
                            else:
                                error = "❌ No reviews found or invalid link."
                    else:
                        error = "❌ Flipkart scraping failed: No file created."

                except Exception as e:
                    error = f"❌ Flipkart scraping failed: {str(e)}"

            else:
                return render_template("index.html", error="❌ Unsupported platform.")

            # ✅ Check if JSON file has reviews
            filepath = os.path.join(BASE_DIR, filename)
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    data = f.read().strip()
                
                reviews = json.loads(data)
                if isinstance(reviews, list) and len(reviews) > 0:
                    message = f"✅ {platform.capitalize()} scraping completed!"
                    file_to_download = filename
                else:
                    error = "❌ No reviews found or invalid link."

            else:
                error = "❌ Scraping failed: No Reviews Found."

        except Exception as e:
            error = f"❌ Scraping failed: {str(e)}"

    return render_template("index.html", message=message, error=error, file=file_to_download)



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



@app.route('/progress')
def get_progress():
    return json.dumps(progress_data)




if __name__ == "__main__":
    app.run(debug=True)

def scrape_flipkart_reviews(product_url: str, progress_callback=None):
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from webdriver_manager.chrome import ChromeDriverManager
    from datetime import datetime, timedelta
    import time, json, os, re

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    filename = os.path.join(BASE_DIR, "flipkart_reviews.json")
    reviews_data = []

    def parse_flipkart_date(date_str):
        date_str = date_str.lower().strip()
        today = datetime.today()

        if "today" in date_str or "just now" in date_str:
            return today.strftime("%d/%m/%Y")
        elif "yesterday" in date_str:
            return (today - timedelta(days=1)).strftime("%d/%m/%Y")
        elif "day" in date_str:
            days_ago = int(re.search(r'\d+', date_str).group())
            return (today - timedelta(days=days_ago)).strftime("%d/%m/%Y")
        elif "week" in date_str:
            weeks_ago = int(re.search(r'\d+', date_str).group())
            return (today - timedelta(weeks=weeks_ago)).strftime("%d/%m/%Y")
        elif "month" in date_str:
            months_ago = int(re.search(r'\d+', date_str).group())
            return (today - timedelta(days=months_ago * 30)).strftime("%d/%m/%Y")
        elif "year" in date_str:
            years_ago = int(re.search(r'\d+', date_str).group())
            return (today - timedelta(days=years_ago * 365)).strftime("%d/%m/%Y")

        for fmt in ["%d %B %Y", "%B %Y", "%b, %Y", "%b %Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                if "%d" not in fmt:
                    dt = dt.replace(day=1)
                return dt.strftime("%d/%m/%Y")
            except ValueError:
                continue

        return "Unknown"

    # For extracting the total number of pages
    def get_total_pages(driver):
        try:
            time.sleep(2)
            pagination = driver.find_element(By.XPATH, "//div[contains(@class, 'mpIySA')]//span[contains(text(), 'Page')]")
            text = pagination.text.strip()  # No indexing needed
            if "of" in text:
                return int(text.split("of")[-1].strip())
            return 1
        except Exception as e:
            print(f"Error in get_total_pages: {e}")
            return 1

    def setup_driver():
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    
    # Extracting reviews from multiple pages
    def extract_reviews():
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'EKFha-')]")))
        reviews = driver.find_elements(By.XPATH, "//div[contains(@class, 'EKFha-')]")
        for review in reviews:
            try:
                date = review.find_element(By.XPATH, ".//p[contains(@class, '_2NsDsF') and not(contains(@class, 'AwS1CA'))]").text.strip()
                clean_date = parse_flipkart_date(date)
            except:
                clean_date = "Unknown"

            try:
                rating = review.find_element(By.XPATH, ".//div[contains(@class, 'XQDdHH')]").text.strip()
            except:
                rating = "N/A"

            try:
                title = review.find_element(By.XPATH, ".//p[contains(@class, 'z9E0IG')]").text.strip()
            except:
                title = "N/A"

            try:
                body = review.find_element(By.XPATH, ".//div[contains(@class, 'ZmyHeo')]").text.strip()
            except:
                body = "N/A"

            reviews_data.append([clean_date, rating, title, body])

    
    # Extracting review from the product page(not having multiple pages)
    def extract_from_product_page():
        wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@class='RcXBOT']")))
        reviews = driver.find_elements(By.XPATH, "//div[@class='RcXBOT']")
        for review in reviews:
            try:
                date = review.find_element(By.XPATH, ".//p[contains(@class, '_2NsDsF') and not(contains(@class, 'AwS1CA'))]").text.strip()
                clean_date = parse_flipkart_date(date)
            except:
                clean_date = "Unknown"

            try:
                rating = review.find_element(By.XPATH, ".//div[@class='XQDdHH Js30Fc Ga3i8K' or @class='XQDdHH Ga3i8K']").text.strip()
            except:
                rating = "N/A"

            try:
                title = review.find_element(By.XPATH, ".//p[@class='z9E0IG']").text.strip()
            except:
                title = "N/A"

            try:
                body = review.find_element(By.XPATH, ".//div[@class='ZmyHeo']").text.strip()
            except:
                body = "N/A"

            reviews_data.append([clean_date, rating, title, body])

            if progress_callback:
                progress_callback(1, 1)

    try:
        driver = setup_driver()
        wait = WebDriverWait(driver, 15)
        driver.get(product_url)
        time.sleep(5)

        # Try clicking the "All Reviews" button
        try:
            all_reviews_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'All') and contains(text(), 'review')]")))
            all_reviews_button.click()
            time.sleep(3)

            MAX_PAGES = get_total_pages(driver)
            page_count = 0

            while True:
                print(f"Scraping page {page_count + 1}")
                extract_reviews()
                page_count += 1

                
                if progress_callback:
                    progress_callback(page_count, MAX_PAGES)

                if page_count >= MAX_PAGES:
                    print("⚠️ Page limit reached. Stopping further scraping.")
                    break
                try:
                    next_button = driver.find_element(By.XPATH, "//nav//a[.//span[text()='Next']]")
                    if next_button.is_enabled():
                        next_button.click()
                        time.sleep(1)
                    else:
                        break
                except:
                    break

        except:
            # Fallback: Extract directly from product page
            extract_from_product_page()

        driver.quit()

    except Exception as e:
        # Save partial data even on error
        print(f"⚠️ Error occurred: {str(e)}")
    finally:
        if reviews_data:
            fieldnames = ["Review_Date", "User_Rating_Out_Of_5", "Review_Title", "Review_Body"]
            reviews_data_dicts = [dict(zip(fieldnames, row)) for row in reviews_data]
            with open(filename, mode="w", encoding="utf-8") as file:
                json.dump(reviews_data_dicts, file, ensure_ascii=False, indent=4)
            return f"✅ Scraping completed! {len(reviews_data_dicts)} reviews saved.", True, reviews_data_dicts
        else:
            return "⚠️ No reviews were found.", False, None

from playwright.sync_api import sync_playwright
import json
import pandas as pd
import time
import random

def safe_goto(page, url, retries=3):
    for i in range(retries):
        try:
            page.goto(url, timeout=60000)
            return True
        except:
            print(f"Retry {i+1}...")
            time.sleep(2)
    return False


def human_behavior(page):
    time.sleep(random.uniform(1.5, 3.5))
    page.mouse.move(random.randint(100, 400), random.randint(100, 400))
    page.mouse.wheel(0, random.randint(300, 800))


def scrape_books(page):
    data = []
    page_num = 1

    while True:
        url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"

        if not safe_goto(page, url):
            break

        page.wait_for_selector(".product_pod")
        books = page.query_selector_all(".product_pod")

        if not books:
            break

        for book in books:
            title = book.query_selector("h3 a").get_attribute("title")
            price = book.query_selector(".price_color").inner_text()

            data.append({
                "title": title,
                "price": price,
                "source": "books"
            })

        human_behavior(page)
        page_num += 1

    return data


def scrape_quotes(page):
    data = []

    if not safe_goto(page, "https://quotes.toscrape.com/"):
        return data

    page.wait_for_selector(".quote")
    quotes = page.query_selector_all(".quote")

    for q in quotes:
        text = q.query_selector(".text").inner_text()
        author = q.query_selector(".author").inner_text()

        data.append({
            "title": text,
            "price": author,
            "source": "quotes"
        })

    return data


def scrape_all():
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent="Mozilla/5.0",
            viewport={"width": 1280, "height": 800}
        )

        page = context.new_page()

        # 🔥 stealth
        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """)

        all_data += scrape_books(page)
        all_data += scrape_quotes(page)

        browser.close()

    # lưu file
    with open("data/products.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    pd.DataFrame(all_data).to_csv("data/products.csv", index=False)

    return all_data
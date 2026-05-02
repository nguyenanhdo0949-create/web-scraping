from playwright.sync_api import sync_playwright
import json
import pandas as pd
import time
import random

def scrape_books(page):
    data = []
    for i in range(1, 3):
        url = f"https://books.toscrape.com/catalogue/page-{i}.html"
        page.goto(url)
        page.wait_for_selector(".product_pod")

        books = page.query_selector_all(".product_pod")

        for book in books:
            title = book.query_selector("h3 a").get_attribute("title")
            price = book.query_selector(".price_color").inner_text()

            data.append({
                "title": title,
                "price": price,
                "source": "books"
            })
    return data


def scrape_quotes(page):
    data = []
    page.goto("https://quotes.toscrape.com/")
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

        time.sleep(random.uniform(1, 2))
        all_data += scrape_books(page)

        time.sleep(random.uniform(1, 2))
        all_data += scrape_quotes(page)

        browser.close()

    with open("data/products.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    df = pd.DataFrame(all_data)
    df.to_csv("data/products.csv", index=False)

    return all_data
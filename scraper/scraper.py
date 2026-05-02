from playwright.sync_api import sync_playwright
import json
import pandas as pd
import time
import random

# =========================
# SAFE NAVIGATION (retry)
# =========================
def safe_goto(page, url, retries=3):
    for i in range(retries):
        try:
            page.goto(url, timeout=60000)
            return True
        except:
            print(f"⚠ Retry {i+1}: {url}")
            time.sleep(2)
    return False


# =========================
# HUMAN BEHAVIOR (anti-bot)
# =========================
def human_behavior(page):
    time.sleep(random.uniform(1, 2))
    try:
        page.mouse.move(random.randint(100, 500), random.randint(100, 500))
        page.mouse.wheel(0, random.randint(200, 600))
    except:
        pass


# =========================
# SCRAPE BOOKS (pagination chuẩn)
# =========================
def scrape_books(page):
    data = []
    page_num = 1

    while True:
        # 👉 FIX URL đúng
        if page_num == 1:
            url = "https://books.toscrape.com/"
        else:
            url = f"https://books.toscrape.com/catalogue/page-{page_num}.html"

        print(f"📄 Crawling page {page_num}...")

        if not safe_goto(page, url):
            print("❌ Không load được trang")
            break

        # 👉 FIX timeout error
        try:
            page.wait_for_selector(".product_pod", timeout=10000)
        except:
            print("🚫 Không tìm thấy sản phẩm → dừng")
            break

        books = page.query_selector_all(".product_pod")

        if not books:
            print("🚫 Hết dữ liệu")
            break

        for book in books:
            try:
                title = book.query_selector("h3 a").get_attribute("title")
                price = book.query_selector(".price_color").inner_text()

                data.append({
                    "title": title,
                    "price": price,
                    "source": "books"
                })
            except:
                continue

        human_behavior(page)
        page_num += 1

    return data


# =========================
# SCRAPE QUOTES
# =========================
def scrape_quotes(page):
    data = []

    url = "https://quotes.toscrape.com/"
    print("💬 Crawling quotes...")

    if not safe_goto(page, url):
        return data

    try:
        page.wait_for_selector(".quote", timeout=10000)
    except:
        print("❌ Không load được quotes")
        return data

    quotes = page.query_selector_all(".quote")

    for q in quotes:
        try:
            text = q.query_selector(".text").inner_text()
            author = q.query_selector(".author").inner_text()

            data.append({
                "title": text,
                "price": author,
                "source": "quotes"
            })
        except:
            continue

    return data


# =========================
# MAIN SCRAPER
# =========================
def scrape_all():
    all_data = []

    with sync_playwright() as p:
        # 👉 DEBUG nếu cần: headless=False
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent="Mozilla/5.0",
            viewport={"width": 1280, "height": 800}
        )

        page = context.new_page()

        # 👉 STEALTH (anti-bot)
        page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        })
        """)

        # 👉 RUN SCRAPERS
        all_data += scrape_books(page)
        all_data += scrape_quotes(page)

        browser.close()

    # =========================
    # SAVE FILE
    # =========================
    with open("data/products.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4, ensure_ascii=False)

    pd.DataFrame(all_data).to_csv("data/products.csv", index=False)

    print(f"✅ Total collected: {len(all_data)}")

    return all_data
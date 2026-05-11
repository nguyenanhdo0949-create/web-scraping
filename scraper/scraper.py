"""
scraper/scraper.py — Playwright scraper với đầy đủ anti-bot stealth.
Thu thập: books.toscrape.com (toàn bộ phân trang).
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.sync_api import sync_playwright
import json, time, random, pandas as pd
from logger import get_logger
from config import DATA_DIR

logger = get_logger("playwright")

# ── Stealth script (vượt anti-bot) ────────────────────────────────────────────
STEALTH_JS = """
() => {
    // webdriver property
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    // plugins
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
    // languages
    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
    // chrome runtime
    window.chrome = { runtime: {} };
    // permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) =>
        parameters.name === 'notifications'
            ? Promise.resolve({ state: Notification.permission })
            : originalQuery(parameters);
}
"""


def safe_goto(page, url, retries=3):
    for i in range(retries):
        try:
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            return True
        except Exception as e:
            logger.warning(f"  Retry {i+1}/{retries}: {url} → {e}")
            time.sleep(2)
    return False


def human_behavior(page):
    """Giả lập hành vi người dùng thật."""
    time.sleep(random.uniform(0.8, 2.0))
    try:
        page.mouse.move(random.randint(100, 800), random.randint(100, 600))
        page.mouse.wheel(0, random.randint(200, 700))
    except Exception:
        pass


def scrape_books(page) -> list[dict]:
    """Crawl toàn bộ books.toscrape.com."""
    data = []
    page_num = 1

    while True:
        url = ("https://books.toscrape.com/"
               if page_num == 1
               else f"https://books.toscrape.com/catalogue/page-{page_num}.html")

        logger.info(f"  [Playwright] Books page {page_num} → {url}")

        if not safe_goto(page, url):
            logger.error("  [Playwright] Cannot load page → stop")
            break

        try:
            page.wait_for_selector(".product_pod", timeout=10000)
        except Exception:
            logger.info("  [Playwright] No products → stop")
            break

        books = page.query_selector_all(".product_pod")
        if not books:
            break

        for book in books:
            try:
                title = book.query_selector("h3 a").get_attribute("title")
                price = book.query_selector(".price_color").inner_text().strip()
                rating_class = book.query_selector(".star-rating").get_attribute("class")
                rating_word = rating_class.replace("star-rating ", "").strip()
                rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
                rating = rating_map.get(rating_word, 0)
                availability = book.query_selector(".availability").inner_text().strip()

                data.append({
                    "title": title,
                    "price": price,
                    "rating": rating,
                    "availability": availability,
                    "scraped_by": "playwright"
                })
            except Exception as e:
                logger.warning(f"  [Playwright] Parse error: {e}")
                continue

        if not page.query_selector(".next a"):
            logger.info("  [Playwright] Last page reached")
            break

        human_behavior(page)
        page_num += 1

    logger.info(f"  [Playwright] Total books collected: {len(data)}")
    return data


def scrape_playwright() -> list[dict]:
    """Entry point — trả về danh sách books."""
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled"
        ])

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
            locale="en-US",
            timezone_id="Asia/Ho_Chi_Minh",
            extra_http_headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            }
        )

        # Inject stealth vào tất cả page
        context.add_init_script(STEALTH_JS)
        page = context.new_page()

        logger.info("[Playwright] Starting books.toscrape.com scraper...")
        all_data = scrape_books(page)

        browser.close()

    # Lưu file
    os.makedirs(DATA_DIR, exist_ok=True)
    json_path = os.path.join(DATA_DIR, "books.json")
    csv_path = os.path.join(DATA_DIR, "books.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2, ensure_ascii=False)
    pd.DataFrame(all_data).to_csv(csv_path, index=False, encoding="utf-8-sig")

    logger.info(f"[Playwright] Saved {len(all_data)} books → {json_path}")
    return all_data
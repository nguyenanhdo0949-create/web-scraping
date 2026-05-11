"""
scraper/selenium_scraper.py — Selenium scraper với ChromeDriver tự động.
Thu thập: quotes.toscrape.com/js/ (trang render bằng JavaScript).
Mục đích: Chứng minh Selenium xử lý được JS-rendered content.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time, random, json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from logger import get_logger
from config import DATA_DIR

logger = get_logger("selenium")


def get_driver() -> webdriver.Chrome:
    """Khởi tạo Chrome driver với anti-bot options."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    # Stealth: ẩn webdriver flag
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            window.chrome = { runtime: {} };
        """
    })

    return driver


def scrape_quotes_js() -> list[dict]:
    """
    Crawl quotes.toscrape.com/js/ — trang dùng JavaScript để render quotes.
    Đây là use-case điển hình của Selenium: đợi JS render xong rồi lấy data.
    """
    data = []
    driver = get_driver()
    wait = WebDriverWait(driver, 15)

    try:
        page_num = 1

        while True:
            url = (
                "https://quotes.toscrape.com/js/"
                if page_num == 1
                else f"https://quotes.toscrape.com/js/page/{page_num}/"
            )
            logger.info(f"  [Selenium] JS-Quotes page {page_num} → {url}")

            driver.get(url)

            # Đợi JavaScript render xong (phần tử .quote xuất hiện)
            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "quote")))
            except Exception:
                logger.info(f"  [Selenium] No quotes on page {page_num} → stop")
                break

            # Random delay giả lập người dùng
            time.sleep(random.uniform(0.5, 1.5))

            quotes = driver.find_elements(By.CLASS_NAME, "quote")
            if not quotes:
                break

            for q in quotes:
                try:
                    text   = q.find_element(By.CLASS_NAME, "text").text.strip()
                    author = q.find_element(By.CLASS_NAME, "author").text.strip()
                    tags   = [t.text.strip() for t in q.find_elements(By.CLASS_NAME, "tag")]

                    data.append({
                        "text":       text,
                        "author":     author,
                        "tags":       ", ".join(tags),
                        "scraped_by": "selenium"
                    })
                except Exception as e:
                    logger.warning(f"  [Selenium] Parse error: {e}")
                    continue

            # Kiểm tra trang kế tiếp
            try:
                driver.find_element(By.CSS_SELECTOR, ".next a")
                page_num += 1
            except Exception:
                logger.info("  [Selenium] Last page reached")
                break

    finally:
        driver.quit()

    logger.info(f"  [Selenium] Total JS-quotes collected: {len(data)}")
    return data


def scrape_selenium() -> list[dict]:
    """Entry point cho Selenium scraper."""
    logger.info("[Selenium] Starting quotes.toscrape.com/js/ scraper...")
    data = scrape_quotes_js()

    # Lưu file
    os.makedirs(DATA_DIR, exist_ok=True)
    json_path = os.path.join(DATA_DIR, "quotes_selenium.json")
    csv_path  = os.path.join(DATA_DIR, "quotes_selenium.csv")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    pd.DataFrame(data).to_csv(csv_path, index=False, encoding="utf-8-sig")

    logger.info(f"[Selenium] Saved {len(data)} quotes → {json_path}")
    return data

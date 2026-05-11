"""
main.py — Entry point chạy toàn bộ pipeline:
  1. Playwright  → crawl books.toscrape.com → SQLite (bảng books)
  2. Selenium    → crawl quotes.toscrape.com/js/ → SQLite (bảng quotes, scraped_by=selenium)
  3. Scrapy      → crawl quotes.toscrape.com → SQLite (bảng quotes, scraped_by=scrapy)
"""
import sys
import os
import time
import subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import create_db, insert_books, insert_quotes
from logger import get_logger

logger = get_logger("main")


def run_scrapy():
    """Chạy Scrapy spider từ subprocess để tránh reactor conflict."""
    scrapy_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "scraper", "scrapy_crawler"
    )
    logger.info("[Scrapy] Launching quotes_spider via subprocess...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "scrapy", "crawl", "quotes_spider"],
            cwd     = scrapy_dir,
            capture_output = True,
            text    = True,
            timeout = 120
        )
        if result.returncode == 0:
            logger.info("[Scrapy] quotes_spider completed successfully")
        else:
            logger.error(f"[Scrapy] Error:\n{result.stderr[-2000:]}")
    except subprocess.TimeoutExpired:
        logger.error("[Scrapy] Timed out after 120s")
    except Exception as e:
        logger.error(f"[Scrapy] Exception: {e}")


def main():
    start = time.time()
    logger.info("=" * 60)
    logger.info("  Web Scraping Project — Full Pipeline Start")
    logger.info("=" * 60)

    # Step 0: Ensure DB schema
    logger.info("[0/4] Khởi tạo database...")
    create_db()

    # Step 1: Playwright → books
    logger.info("[1/4] Playwright → books.toscrape.com...")
    try:
        from scraper.scraper import scrape_playwright
        books = scrape_playwright()
        insert_books(books)
        logger.info(f"  ✓ Đã lưu {len(books)} sách vào DB")
    except Exception as e:
        logger.error(f"  ✗ Playwright thất bại: {e}")

    # Step 2: Selenium → quotes (JS-rendered)
    logger.info("[2/4] Selenium → quotes.toscrape.com/js/ ...")
    try:
        from scraper.selenium_scraper import scrape_selenium
        quotes_sel = scrape_selenium()
        insert_quotes(quotes_sel)
        logger.info(f"  ✓ Đã lưu {len(quotes_sel)} quotes (Selenium) vào DB")
    except Exception as e:
        logger.error(f"  ✗ Selenium thất bại: {e}")

    # Step 3: Scrapy → quotes (static HTML, via subprocess)
    logger.info("[3/4] Scrapy → quotes.toscrape.com ...")
    run_scrapy()

    elapsed = round(time.time() - start, 2)
    logger.info("=" * 60)
    logger.info(f"  Pipeline hoàn tất trong {elapsed}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
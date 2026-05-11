"""
Scrapy Pipelines — tương thích Scrapy 2.11+
  1. JsonFilePipeline  — ghi ra data/quotes_scrapy.json
  2. DbPipeline        — lưu thẳng vào SQLite (bảng quotes)
"""
import json
import os
import sqlite3


def _get_project_root() -> str:
    """
    pipelines.py: <root>/scraper/scrapy_crawler/quotes_crawler/pipelines.py
    3 bước lên: quotes_crawler → scrapy_crawler → scraper → <root>
    """
    here = os.path.dirname(os.path.abspath(__file__))   # quotes_crawler/
    scrapy_crawler = os.path.dirname(here)               # scrapy_crawler/
    scraper = os.path.dirname(scrapy_crawler)            # scraper/
    return os.path.dirname(scraper)                      # project root


def _get_db_path() -> str:
    return os.path.join(_get_project_root(), "database", "products.db")


def _get_data_dir() -> str:
    data_dir = os.path.join(_get_project_root(), "data")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


# ── Pipeline 1: JSON file ─────────────────────────────────────────────────────

class JsonFilePipeline:

    def open_spider(self, spider=None):
        self.path = os.path.join(_get_data_dir(), "quotes_scrapy.json")
        self.items = []

    def close_spider(self, spider=None):
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.items, f, indent=2, ensure_ascii=False)
        if spider:
            spider.logger.info(f"[JsonFilePipeline] Saved {len(self.items)} items → {self.path}")

    def process_item(self, item, spider=None):
        self.items.append(dict(item))
        return item


# ── Pipeline 2: SQLite DB ─────────────────────────────────────────────────────

class DbPipeline:

    def open_spider(self, spider=None):
        db_path = _get_db_path()
        self.conn = None

        if not os.path.exists(db_path):
            if spider:
                spider.logger.error(f"[DbPipeline] DB not found: {db_path} — run main.py first!")
            return

        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.cursor = self.conn.cursor()
        self.cursor.execute("DELETE FROM quotes WHERE scraped_by='scrapy'")
        self.conn.commit()
        if spider:
            spider.logger.info("[DbPipeline] Connected, cleared old scrapy quotes")

    def close_spider(self, spider=None):
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def process_item(self, item, spider=None):
        if not self.conn:
            return item
        self.cursor.execute(
            "INSERT INTO quotes (text, author, tags, scraped_by) VALUES (?, ?, ?, ?)",
            (
                item.get("text", ""),
                item.get("author", ""),
                item.get("tags", ""),
                item.get("scraped_by", "scrapy"),
            )
        )
        return item

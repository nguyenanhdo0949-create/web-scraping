"""
Scrapy Middlewares — tương thích Scrapy 2.11+
"""
import random
from scrapy import signals


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
]


class RandomUserAgentMiddleware:
    """Xoay vòng User-Agent để tránh bị block — Scrapy 2.11+ API."""

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider=None):
        request.headers["User-Agent"] = random.choice(USER_AGENTS)

    def spider_opened(self, spider=None):
        if spider:
            spider.logger.info("[Middleware] RandomUserAgent enabled")

import scrapy
from quotes_crawler.items import QuoteItem


class QuotesSpider(scrapy.Spider):
    """
    Spider thu thập dữ liệu từ quotes.toscrape.com (static HTML).
    Crawl toàn bộ phân trang tự động qua next-page link.
    """
    name = "quotes_spider"
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
    }

    def parse(self, response):
        self.logger.info(f"Parsing page: {response.url}")

        for q in response.css(".quote"):
            item = QuoteItem()
            item["text"]       = q.css(".text::text").get("").strip()
            item["author"]     = q.css(".author::text").get("").strip()
            item["tags"]       = ", ".join(q.css(".tag::text").getall())
            item["scraped_by"] = "scrapy"
            yield item

        # Theo dõi trang kế tiếp tự động
        next_page = response.css(".next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

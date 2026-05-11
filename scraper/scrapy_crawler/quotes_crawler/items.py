# pyrefly: ignore [missing-import]
import scrapy


class QuoteItem(scrapy.Item):
    text       = scrapy.Field()
    author     = scrapy.Field()
    tags       = scrapy.Field()
    scraped_by = scrapy.Field()

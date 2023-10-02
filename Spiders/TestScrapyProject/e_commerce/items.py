import scrapy
from scrapy.loader import ItemLoader


class ProductItem(scrapy.Item):
    identifier = scrapy.Field()
    base_sku = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    category_names = scrapy.Field()
    language_code = scrapy.Field()
    country_code = scrapy.Field()
    currency = scrapy.Field()
    price = scrapy.Field()
    image_urls = scrapy.Field()
    description = scrapy.Field()
    color = scrapy.Field()
    sizes = scrapy.Field()
    availability = scrapy.Field()


class SizeItem(scrapy.Item):
    identifier = scrapy.Field()
    producerSize = scrapy.Field()
    marketSize = scrapy.Field()
    stock = scrapy.Field()
    price = scrapy.Field()


class PriceItem(scrapy.Item):
    original = scrapy.Field()
    final = scrapy.Field()


class ProductLoader(ItemLoader):
    pass

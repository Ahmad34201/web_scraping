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

    @classmethod
    def create(cls, response, id, url, categories):
        return cls(
            identifier=id,
            category_names=categories,
            country_code=response.meta.get('country_code', ''),
            language_code=response.meta.get('language_code', ''),
            currency=response.meta.get('currency', ''),
            url=url
        )


class SizeItem(scrapy.Item):
    identifier = scrapy.Field()
    producerSize = scrapy.Field()
    marketSize = scrapy.Field()
    stock = scrapy.Field()
    price = scrapy.Field()


class PriceItem(scrapy.Item):
    original = scrapy.Field()
    discounted = scrapy.Field()

    @classmethod
    def create(cls, actual, discount):
        return cls(
            original=actual,
            discounted=discount
        )


class ProductLoader(ItemLoader):
    pass


# class MiniItem(scrapy.Item):
#     thumbnail_id = scrapy.Field()
#     country = scrapy.Field()
#     language_of_text = scrapy.Field()
#     currency = scrapy.Field()
#     category_names = scrapy.Field()
#     item_url = scrapy.Field()

#     @classmethod
#     def create(cls, response, id, url, categories):
#         return cls(
#             thumbnail_id = id,
#             category_names = categories,
#             country = response.meta.get('country_code', ''),
#             language_of_text = response.meta.get('language_code', ''),
#             currency = response.meta.get('currency', ''),
#             item_url = url
#         )
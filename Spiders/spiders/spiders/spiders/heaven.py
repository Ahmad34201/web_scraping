import json
from copy import deepcopy
import scrapy
from scrapy.loader import ItemLoader
from ..items import ProductItem, SizeItem, PriceItem, ProductLoader
from ..utils import *


class HeavenSpider(scrapy.Spider):
    de__countries_info = [
        # ('country', 'currency', 'language', 'url')
        ('gb', 'GBP', 'en', "https://www.marcjacobs.com/"),
    ]
    name = 'heaven'

    def start_requests(self):
        for country_code, currency, language, country_url in self.de__countries_info:

            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
            }

            yield scrapy.Request(country_url, self.de__parse_top_cats, meta=meta)

    def de__parse_top_cats(self, response):
        for level1 in response.xpath('//ul[@class="nav-modal__sub-list"]'):
            print("len", len(level1))
            # yield self.de__make_navigation_request(response, [level1])

            # for level2 in level1.xpath('//ul[@class="hasFeaturedImg"]/li'):
            #     yield self.de__make_navigation_request(response, [level1, level2])

    def de__make_navigation_request(self, response, selectors):
        categories = [sel.css('a::text').get('').strip() for sel in selectors]
        url = selectors[-1].css('a::attr(href)').get()
        if not url:
            return
        print("Categories ", categories)
        meta = deepcopy(response.meta)
        meta['categories'] = categories
        return None

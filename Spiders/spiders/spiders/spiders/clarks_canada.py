import scrapy
from ..items import ProductItem, SizeItem, PriceItem, ProductLoader
from ..utils import *
import json
from scrapy.loader import ItemLoader
from copy import deepcopy
import json


class clarkSpider(scrapy.Spider):
    de__countries_info = [
        # ('country', 'currency', 'language', 'url')
        ('gb', 'GBP', 'en', "https://www.clarks.com/en-ca"),
    ]
    name = 'clarks_canada'

    def start_requests(self):
        for country_code, currency, language, country_url in self.de__countries_info:

            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
            }

            yield scrapy.Request(country_url, self.de__parse_top_cats, meta=meta)

    def de__parse_top_cats(self, response):
        for level1 in response.xpath('//div[@class="r2d2-sub-nav"]'):
            yield self.de__make_navigation_request(response, [level1])
            
            for level2 in level1.xpath('//ul/li[@class="r2d2-nav-list_item"]'):
                yield self.de__make_navigation_request(response, [level1, level2])
                

    def de__make_navigation_request(self, response, selectors):
        categories = [sel.css('a::text').get('').strip() for sel in selectors]
        url = selectors[-1].css('a::attr(href)').get()
        if not url:
            return
        print("Categories ", categories)
        meta = deepcopy(response.meta)
        meta['categories'] = categories
        return None

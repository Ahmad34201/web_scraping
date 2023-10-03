import scrapy
from ..items import ProductItem, SizeItem, PriceItem, ProductLoader
from ..utils import *
import json
from scrapy.loader import ItemLoader
from copy import deepcopy
from w3lib.url import add_or_replace_parameter


class MinttoSpider(scrapy.Spider):
    de__countries_info = [
        # ('country', 'currency', 'language', 'url')
        ('gb', 'GBP', 'en', 'https://www.miinto.co.uk'),
    ]
    name = 'mintto_co'
    total_pages = 0
    category_thumbnail_counts = {}  # Initialize an empty dictionary to store counts

    def start_requests(self):
        for country_code, currency, language, country_url in self.de__countries_info:

            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
                'dont_merge_cookies': True,
            }

            yield scrapy.Request(country_url, self.de__parse_top_cats, meta=meta)

    def de__parse_top_cats(self, response):

        total_level1_cat = len(response.css(
            'nav[data-testid="desktop-navigation"]>ul'))
        for l1_cat in range(1, total_level1_cat+1):
            level1 = response.css(
                'ul[data-testid="desktop-navigation-{}"]'.format(l1_cat))
            yield self.de__make_navigation_request(response, [level1])

            total_level2_cat = len(level1.css(
                'ul[data-testid="desktop-navigation-{}-items"]>li'.format(l1_cat)))
            for l2_cat in range(1, total_level2_cat+1):
                level2 = level1.css(
                    'li[data-testid="desktop-navigation-{}-items-item-{}"]'.format(l1_cat, l2_cat))
                yield self.de__make_navigation_request(response, [level1, level2])

                total_level3_cat = len(level2.css(
                    'ul[data-testid="desktop-navigation-{}-{}-1-items"]>li'.format(l1_cat, l2_cat)))
                for l3_cat in range(1, total_level3_cat+1):
                    level3 = level2.css(
                        'li[data-testid="desktop-navigation-{}-{}-1-items-item-{}"]'.format(l1_cat, l2_cat, l3_cat))
                    yield self.de__make_navigation_request(response, [level1, level2, level3])

    def de__make_navigation_request(self, response, selectors):
        categories = [sel.css('a::text').get('').strip() for sel in selectors]
        url = selectors[-1].css('a::attr(href)').get()
        if not url:
            return
        main_url = urljoin(response.url, url)
        meta = deepcopy(response.meta)
        meta['categories'] = categories
        return scrapy.Request(main_url, callback=self.de_make_pagination, meta=meta)

    @staticmethod
    def validate_response(request, response, spider):
        return bool(response.css('.c-product-card'))

    
    def de_make_pagination(self, response):
        self.set_total_pages(response)
        categories = response.meta.get('categories', [])
        thumbnail_count = len(response.css('.c-fVIQI').getall())
        self.update_category_thumbnail_counts(categories, thumbnail_count)
        # next_page_request = self.generate_next_page_request(
        #     response, categories)

        for thumbnail_id in range(1, thumbnail_count + 1):
            thumbnail_selector = response.css('div[data-testid="product-{}"]'.format(thumbnail_id))
            thumbnail_url = thumbnail_selector.css('a::attr(href)').get()
            # yield MiniItem.create(response, categories, urljoin(response.url,thumbnail_url))

        # if next_page_request:
        #     yield next_page_request

    def generate_next_page_request(self, response, categories):
        current_page = response.meta.get('page', 1)
        if current_page < self.total_pages:
            next_page_number = current_page + 1
            paginated_url = add_or_replace_parameter(
                response.url, 'page', next_page_number)
            meta = deepcopy(response.meta)
            meta['categories'] = categories
            meta['page'] = next_page_number

            return scrapy.Request(paginated_url, callback=self.de_make_pagination, meta=meta)
        return None

    def update_category_thumbnail_counts(self, categories, thumbnail_count):
        category_key = "_".join(categories)
        if category_key not in self.category_thumbnail_counts:
            self.category_thumbnail_counts[category_key] = 0
        self.category_thumbnail_counts[category_key] += thumbnail_count

    def set_total_pages(self, response):
        total_pages_text = response.css(
            'p[data-testid="pagination-text"]::text').getall()
        if total_pages_text:
            self.total_pages = int(total_pages_text[-1])

    def closed(self, reason):
        for category, count in self.category_thumbnail_counts.items():
            self.crawler.stats.set_value(f'thumbnail_count_{category}', count)

        for category, count in self.category_thumbnail_counts.items():
            print(f"Thumbnail count for {category}: {count}")

        print("Spider closed:", reason)

    
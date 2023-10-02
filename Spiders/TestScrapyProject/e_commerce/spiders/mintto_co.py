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
        # ('fi', 'EUR', 'fi', 'https://www.miinto.fi/brands'),
        # ('dk', 'DKK', 'da', 'https://www.miinto.dk/brands'),
        # ('de', 'EUR', 'de', 'https://www.miinto.de/brands'),
        # ('nl', 'EUR', 'nl', 'https://www.miinto.nl/brands'),
        # ('no', 'NOK', 'no', 'https://www.miinto.no/brands'),
        # ('se', 'SEK', 'sv', 'https://www.miinto.se/brands'),
        # ('be', 'EUR', 'be', 'https://www.miinto.be/brands'),
        # ('ch', 'CHF', 'de', 'https://www.miinto.ch/brands'),
        # ('fr', 'EUR', 'fr', 'https://www.miinto.fr/brands'),
        ('gb', 'GBP', 'en', 'https://www.miinto.co.uk'),
        # ('it', 'EUR', 'it', 'https://www.miinto.it/brands'),
        # ('pl', 'PLN', 'pl', 'https://www.showroom.pl/brands'),
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

    # def parse_detailed_page(self, response):
    #     # Extract product URLs and initiate parsing
    #     all_products = response.css('a.c-dvHMYx::attr(href)').getall()
    #     for url in all_products:
    #         yield scrapy.Request(urljoin(response.url, url), callback=self.parse_product)

    # def parse_product(self, response):
    #     loader = ProductLoader(item=ProductItem(), response=response)
    #     loader.add_value('product_url', extract_product_url(response))
    #     item = self.get_item(response)
    #     self.load_product_data(loader, item)
    #     yield loader.load_item()

    # def get_item(self, response):
    #     script_text = response.xpath(
    #         '//script[contains(., "window.__PDP_PRELOADED_STATE__")]/text()').get()
    #     if script_text:
    #         json_start = script_text.find('JSON.stringify(')
    #         json_end = script_text.find(');', json_start)
    #         if json_start != -1 and json_end != -1:
    #             json_string = script_text[json_start +
    #                                       len('JSON.stringify('):json_end]
    #             try:
    #                 item_data = json.loads(json_string)
    #                 return item_data['product']
    #             except json.JSONDecodeError as e:
    #                 self.logger.error(f"JSON decoding error: {e}")
    #     return {}

    # def load_product_data(self, loader, item):
    #     loader.add_value('brand', item.get('brand'))
    #     loader.add_value('title', item.get('title'))
    #     loader.add_value('color', item.get('productColor'))
    #     self.load_price(loader, item)
    #     self.load_sizes(loader, item)
    #     loader.add_value('image_urls', self.extract_image_urls(item))
    #     loader.add_value('description', item.get('description'))
    #     loader.add_value('categories', item.get('categoryId'))

    # def load_price(self, loader, item):
    #     price_item = PriceItem()
    #     price_item['original'] = item['price']['originalPrice']
    #     price_item['discounted'] = item['price']['price']
    #     loader.add_value('price', price_item)

    # def extract_image_urls(self, item):
    #     images = item.get('images', [])
    #     return [image.get("url") for image in images]

    # def load_sizes(self, loader, item):
    #     sizes = item.get('sizes', [])
    #     size_items = []
    #     for size in sizes:
    #         size_item = SizeItem()
    #         size_item['identifier'] = size.get('miintoId')
    #         size_item['producerSize'] = size.get('producerSize')
    #         size_item['marketSize'] = size.get('marketSize')
    #         size_item['stock'] = size.get('isLastItem')
    #         size_item['price'] = size.get('price')
    #         size_items.append(size_item)
    #     loader.add_value('sizes', size_items)

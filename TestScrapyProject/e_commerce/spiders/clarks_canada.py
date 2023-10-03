import hashlib
from copy import deepcopy
import re
from urllib.parse import urljoin

import scrapy

from ..items import ProductItem


class ClarkSpider(scrapy.Spider):
    name = 'clarks_canada'

    countries_info = [
        # ('country', 'currency', 'language', 'url')
        ('gb', 'GBP', 'en', "https://www.clarks.com/en-ca"),
    ]

    def start_requests(self):
        for country_code, currency, language, country_url in self.countries_info:
            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
            }
            yield scrapy.Request(country_url, self.parse_top_categories, meta=meta)

    def parse_top_categories(self, response):
        for level1 in response.css(".r2d2-sub-nav"):
            level1_cat = level1.css(".r2d2-nav_heading::text").get('')
            yield from self.make_navigation_request(response, '', level1_cat)

            for level2 in level1.css('.r2d2-nav_list>li'):
                level2_cat = level2.css("a::text").get('')
                level2_cat_url = level2.css('a::attr(href)').get()
                yield from self.make_navigation_request(response, level2_cat_url, [level1_cat, level2_cat])

    def make_navigation_request(self, response, cat_url, categories):
        if not cat_url:
            return
        meta = deepcopy(response.meta)
        meta['categories'] = categories
        meta['cat_url'] = urljoin(response.url, cat_url)
        yield scrapy.Request(meta['cat_url'], callback=self.make_pagination, meta=meta)

    def make_pagination(self, response):
        page_num_text = response.css(".sc-b9de3f21-5::text").get()
        last_page = self.get_last_page(page_num_text)
        paginated_url = f'{response.url}?page={last_page}'
        yield scrapy.Request(paginated_url, callback=self.parse_products, meta=response.meta)

    def get_last_page(self, page_num_text):
        numbers = re.findall(r'\d+', page_num_text)
        if len(numbers) >= 2:
            total_pages = int(numbers[1])
            return (total_pages + 71) // 72
        return None

    def parse_products(self, response):
        for product in response.css('.sc-e188e0db-1'):
            mini_item = self.create_initial_item(response, product)
            yield mini_item
            meta = deepcopy(response.meta)
            meta['item'] = mini_item
            yield scrapy.Request(mini_item['url'], self.parse_colors, meta=meta)

    def create_initial_item(self, response, product):
        item_url = urljoin(response.url, product.css('a::attr(href)').get(''))
        categories = response.meta.get('categories', [])
        return ProductItem(
            base_sku=self.get_base_sku(item_url),
            url=item_url,
            category_names=categories,
            country_code=response.meta.get('country_code', ''),
            language_code=response.meta.get('language_code', ''),
            currency=response.meta.get('currency', '')
        )

    def parse_colors(self, response):
        meta = deepcopy(response.meta)
        colored_items = response.css('.sc-44900a7b-0>a::attr(href)').getall()
        for color_url in colored_items:
            url_to_parse = urljoin(response.url, color_url)
            yield scrapy.Request(url_to_parse, self.parse_detail, meta=meta)

    def parse_detail(self, response):
        item = response.meta.get('item')
        item['url'] = response.url
        item['base_sku'] = self.get_base_sku(item['url'])
        item['color'] = self.get_color(response)
        item['identifier'] = self.get_identifier(
            item['base_sku'], item['color'])
        item['title'] = response.css('.sc-29d6aa1f-0::text').get()
        item['price'] = response.css('.sc-a1167b0b-1::text').get()
        item['availability'] = bool(item['color'])
        item['image_urls'] = response.css(
            '.sc-a99bb818-3>span>img::attr(src)').getall()
        item['sizes'] = response.css('.sc-36535bff-2::text').getall()
        item['description'] = response.css('.sc-afae01d3-3::text').get()
        return item

    def get_identifier(self, base_sku, color):
        return f'{base_sku}_{color}'

    def get_base_sku(self, url):
        common_title = url.split('/')[-2]
        base_sku = self.md5_hash(common_title)
        return base_sku

    def get_color(self, response):
        color_availability_text = response.css('.sc-95ff6051-2::text').get()
        color_name = re.search(
            r'colours? available:\s*([A-Za-z]+)', color_availability_text, re.IGNORECASE)
        return color_name.group(1) if color_name else ''

    @staticmethod
    def md5_hash(s, truncate=16):
        md5 = hashlib.md5(s.encode('utf-8')).hexdigest().upper()
        return md5[:truncate]

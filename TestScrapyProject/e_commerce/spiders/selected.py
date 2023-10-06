import re
import json
from copy import deepcopy
from urllib.parse import urljoin

from scrapy import Request, Spider

from ..items import ProductItem, SizeItem


class SelectedSpider(Spider):
    name = 'selected'
    PAGINATION_API = 'https://www.selected.com/on/demandware.store/Sites-sl-Site/en_GB/Search-UpdateGrid?cgid='
    countries_info = [
        ('gb', 'GBP', 'en', "https://www.selected.com/en-gb/home")]

    PAGE_TEXT_PATTERN = re.compile(r'\d+')

    def start_requests(self):
        for country_code, currency, language, country_url in self.countries_info:
            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
            }
            yield Request(country_url, self.parse_top_categories, meta=meta)

    def parse_top_categories(self, response):
        for level1 in response.xpath('//div[contains(@class, "menu-burger__category--root")]/p'):
            level1_subcat = self.parse_subcat(response, level1)
            yield from self.make_navigation_request(response, [level1])

            for level2 in level1_subcat.xpath('p[contains(@class, "category-level-2")]'):
                level2_subcat = self.parse_subcat(response, level2)
                yield from self.make_navigation_request(response, [level1, level2])

                for level3 in level2_subcat.xpath('p[contains(@class, "category-level-3")]'):
                    yield from self.make_navigation_request(response, [level1, level2, level3])

    def make_navigation_request(self, response, selectors):
        cat_url = selectors[-1].css('a::attr(href)').get()
        if not cat_url:
            return

        meta = response.meta.copy()
        categories = [sel.css('a::text').get().strip() for sel in selectors]
        cat_id = selectors[-1].attrib.get('data-category-item-id', '')
        meta.update({'categories': categories,
                     'cat_url': urljoin(
                         response.url, cat_url), 'cat_id': cat_id
                     })
        yield Request(f'{self.PAGINATION_API}{cat_id}&start=0&sz=60', callback=self.parse_pagination, meta=meta)

    def parse_pagination(self, response):
        total_pages = self.parse_total_pages(response)
        meta = response.meta.copy()
        cat_id = meta['cat_id']
        for start in range(0, total_pages, 60):
            yield Request(f'{self.PAGINATION_API}{cat_id}&start={start}&sz=60', callback=self.parse_products, meta=meta)

    def parse_products(self, response):
        for product in response.css('.product-grid-item'):
            item = self.create_product_item(response, product)
            yield item
            yield Request(item['url'], self.parse_colors, meta={'item': item, 'text_to_replace': product.attrib['data-id']})

    def create_product_item(self, response, sel_prod):
        return ProductItem(
            base_sku=sel_prod.attrib['data-id'].split('_')[0],
            url=self.get_item_url(response, sel_prod),
            referer_url=response.url,
            category_names=response.meta['categories'],
            language_code=response.meta['language_code'],
            country_code=response.meta['country_code'],
            currency=response.meta['currency'],
        )

    def get_item_url(self, response, sel_prod):
        return urljoin(response.url, sel_prod.css('.product-tile__image-container > a::attr(href)').get())

    def parse_colors(self, response):
        item = response.meta['item']
        colors = response.css(
            '.product-attributes--color-swatch::attr("data-attr-value")').getall()
        for color in colors:
            url_to_parse = response.url.replace(
                response.meta['text_to_replace'], color)
            yield Request(url_to_parse, self.parse_detail, meta={'item': item})

    def parse_detail(self, response):
        item = response.meta['item']
        identifier = response.css('.js-product-id::text').get()
        item.update({
            'title': response.css('.product-header__name::text').get(),
            'identifier': identifier,
            'color': self.get_color(identifier),
            'base_sku': self.get_base_sku(identifier),
            'price': response.css('.price .value::text').get(),
            'description': response.css('.product-content__text::text').get(),
        })

        yield from self.parse_sizes(response, item)

    def parse_sizes(self, response, item):
        button_urls = response.css(
            '.product-attribute__button--nonswatch::attr("data-url")').getall()
        first_valid_url = next((url for url in button_urls if url), None)
        if first_valid_url:
            yield Request(first_valid_url, callback=self.create_size_item, meta={'item': item})

    def create_size_item(self, response):
        meta = deepcopy(response.meta)
        item = meta['item']
        data = json.loads(response.body)
        product = data.get('product', {})
        attributes = product.get('variationAttributes', [])

        image_urls = self.extract_image_urls(product)
        sizes = [
            SizeItem(
                identifier=size['id'],
                producerSize=size['value'],
                stock=size['orderable'],
            )
            for attribute in attributes if attribute.get('attributeId') == 'size'
            for size in attribute.get('values', [])
        ]

        item['sizes'] = sizes
        item['image_urls'] = image_urls
        return item

    def extract_image_urls(self, product):
        images = product.get('images', {})
        image_urls = {size_key: [url_dict['url'] for url_dict in urls]
                      for size_key, urls in images.items()}
        return image_urls

    @staticmethod
    def get_color(identifier):
        return identifier.split('_')[1] if identifier else None

    @staticmethod
    def get_base_sku(identifier):
        return identifier.split('_')[0] if identifier else None

    def parse_subcat(self, response, level):
        cat_id = level.xpath('@data-category-item-id').get()
        return response.xpath(f'//div[contains(@data-category-id, "{cat_id}")]')

    def parse_total_pages(self, response):
        page_text = response.css('.product-grid-paging__message::text').get()
        if page_text:
            return int(self.PAGE_TEXT_PATTERN.findall(page_text)[1])

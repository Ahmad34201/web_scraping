import json
from copy import deepcopy

from scrapy import Request, Spider

from ..items import ProductItem, SizeItem, PriceItem
from ..utils import *


class clarkSpider(Spider):
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

            yield Request(country_url, self.de__parse_top_cats, meta=meta)

    def de__parse_top_cats(self, response):

        for level1 in response.css(".r2d2-sub-nav"):
            level1_cat = level1.css(".r2d2-nav_heading::text").get('')
            yield from self.de__make_navigation_request(response, '', level1_cat)

            for level2 in level1.css('.r2d2-nav_list>li'):
                level2_cat = level2.css("a::text").get('')
                level2_cat_url = level2.css('a::attr(href)').get()
                yield from self.de__make_navigation_request(response, level2_cat_url, [level1_cat, level2_cat])

    def de__make_navigation_request(self, response, cat_url, categories):
        if not cat_url:
            return
        meta = deepcopy(response.meta)
        meta['categories'] = categories
        meta['cat_url'] = urljoin(response.url, cat_url)
        yield Request(meta['cat_url'], callback=self.de_make_pagination, meta=meta)

    def de_make_pagination(self, response):
        page_num_text = response.css(".sc-b9de3f21-5::text").get()
        last_page = self.get_last_page(page_num_text)

        paginated_url = f'{response.url}?page={last_page}'

        yield Request(paginated_url, callback=self.de__parse_products, meta=response.meta)

    def get_last_page(self, page_num_text):
        match = re.search(r'\d+', page_num_text)
        if match:
            numbers = re.findall(r'\d+', page_num_text)
            if len(numbers) >= 2:
                total_pages = int(numbers[1])
                return (total_pages + 71) // 72
        return None

    def de__parse_products(self, response):
        for product in response.css('.sc-e188e0db-1'):
            mini_item = self.de__create_initial_item(response, product)
            yield mini_item
            meta = deepcopy(response.meta)
            meta['item'] = mini_item
            yield Request(mini_item['url'], self.de__parse_detail, meta=meta)

    def de__create_initial_item(self, response, product):
        item_url = urljoin(response.url, product.css('a::attr(href)').get(''))
        categories = response.meta.get('categories', [])
        return ProductItem(
            identifier=product.css('[id]::attr(id)').get(''),
            url=item_url,
            category_names=categories,
            country_code=response.meta.get('country_code', ''),
            language_code=response.meta.get('language_code', ''),
            currency=response.meta.get('currency', '')
        )

    def de__parse_detail(self, response):
        item = response.meta.get('item')
        item['title'] = response.css('.sc-29d6aa1f-0::text').get()
        item['description'] = response.css('.sc-afae01d3-3::text').get()
        # item['base_sku'] = response_item['sku']
        item['price'] = response.css('.sc-a1167b0b-1::text').get()
        item['image_urls'] = self.de__get_image_urls(response)
        # item['availability'] = self.check_availability(response_item)
        item['sizes'] = response.css('.sc-36535bff-2::text').getall()
        return item

    def de__get_image_urls(self, response):
        return response.xpath('//div[contains(@class, "sc-a99bb818-3")]/span/img/@src').getall()

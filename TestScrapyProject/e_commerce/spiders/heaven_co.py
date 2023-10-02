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
        # have to pass meta['cat_url']
        test_url = "https://www.clarks.com/en-ca/all-mens-styles/mens-comfort-styles/m_comfort_ca-c"
        yield Request(test_url, callback=self.de_make_pagination, meta=meta)

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
            item = self.de__create_initial_item(response, product)
            meta = deepcopy(response.meta)
            meta['item'] = item
            # meta['response_validation_func'] = self.validate_detail
            # yield Request(item['url'], self.de__parse_detail, meta=meta)
            break
    
    def de__create_initial_item(self, response, product):
        item_url = product.css('a::attrib(href)').get('')
        categories = response.meta.get('categories', [])
        print("url ", item_url)
        print("cat", categories)
        print("identifier", product.css('::attrib(id)').get(''))
        return ProductItem(
            identifier=product.css('attrib(id)'),
            url=item_url,
            category_names=categories,
            country_code=response.meta.get('country_code', ''),
            language_code=response.meta.get('language_code', ''),
            currency=response.meta.get('currency', '')
        )
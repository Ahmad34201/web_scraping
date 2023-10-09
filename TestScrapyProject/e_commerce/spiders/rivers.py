import re
import json
from copy import deepcopy
from urllib.parse import urljoin

from scrapy import Request, Spider

from ..items import ProductItem, SizeItem


class RiverSpider(Spider):
    name = 'river'
    PAGE_NUM_REGEX = re.compile(r'\b(\d+)\b')
    countries_info = [
        ('gb', 'GBP', 'en', "https://www.riverisland.com/")]

    def start_requests(self):
        for country_code, currency, language, country_url in self.countries_info:
            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
            }
            yield Request(country_url, self.parse_top_categories, meta=meta)

    def parse_top_categories(self, response):
        for top_cat in response.css('li.mega-menu__item'):
            top_cat_txt = top_cat.css('a span::text').get().strip()
            top_cat_url = top_cat.css(
                'a.main-navigation__item::attr(href)').get()
            yield from self.make_navigation_request(response, [top_cat_txt], top_cat_url)

            for level1 in top_cat.css('div[data-level="1"]>div>ul>li'):
                cat1_txt = level1.css('p::text').get()
                yield from self.make_navigation_request(response, [top_cat_txt, cat1_txt], cat_url="")

                for level2 in level1.css('div[data-level="2"]>ul>li'):
                    cat2_txt, cat2_url = self.parse_category(level2)
                    yield from self.make_navigation_request(response, [top_cat_txt, cat1_txt, cat2_txt], cat2_url)

                    for level3 in level2.css('div[data-level="3"]>ul>li'):
                        cat3_txt, cat3_url = self.parse_category(level3)
                        yield from self.make_navigation_request(
                            response,
                            [top_cat_txt, cat1_txt, cat2_txt, cat3_txt],
                            cat3_url
                        )

    def make_navigation_request(self, response, categories, cat_url):
        if not cat_url:
            return

        meta = response.meta.copy()
        meta.update({'categories': categories,
                     'cat_url': urljoin(
                         response.url, cat_url)
                     })

        yield Request('https://www.riverisland.com/c/women/coats-and-jackets', callback=self.parse_pagination, meta=meta)

    def parse_pagination(self, response):
        page_num_txt = response.css('div[data-qa="product-count"]::text').get()
        last_page = self.get_last_page(page_num_txt)
        for current_page in range(1, last_page+1):
            paginated_url = f'{response.url}?pg={current_page}'
            yield Request(paginated_url, callback=self.parse_products, meta=response.meta)
    
    def parse_products(self, response):
        for product in response.css('a.card___366wY'):
            mini_item = self.create_initial_item(response, product)
            yield mini_item
            meta = deepcopy(response.meta)
            meta['item'] = mini_item
    
    def create_initial_item(self, response, product):
        item_url = urljoin(response.url, product.css('::attr(href)').get(''))
        categories = response.meta.get('categories', [])
        return ProductItem(
            identifier=product.css('::attr("data-id")').get(''),
            url=item_url,
            category_names=categories,
            country_code=response.meta.get('country_code', ''),
            language_code=response.meta.get('language_code', ''),
            currency=response.meta.get('currency', '')
        )

    def get_last_page(self, page_num_txt):
        numbers = self.PAGE_NUM_REGEX.findall(page_num_txt)
        if numbers:
            total_pages = int(numbers[0])
            return (total_pages + 59) // 60
        return None

    def parse_category(self, level):
        cat_txt = level.css('a::text').get().strip()
        cat_url = level.css('a::attr(href)').get()
        return cat_txt, cat_url

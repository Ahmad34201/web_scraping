import re
import hashlib
from copy import deepcopy
from urllib.parse import urljoin

from scrapy import Request, Spider

from ..items import ProductItem, SizeItem


class RiverSpider(Spider):
    name = 'river'
    PAGE_NUM_REGEX = re.compile(r'\b(\d+)\b')
    COLOR_PATTERN = re.compile(r'/p/([a-zA-Z-]+)-\d+')
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
        yield Request(meta['cat_url'], callback=self.parse_pagination, meta=meta)

    def parse_pagination(self, response):
        page_num_txt = response.css('div[data-qa="product-count"]::text').get()
        if page_num_txt:
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
            available_colors = product.css(
                'li.swatch___XcHT_ div>img::attr(alt)').getall()
            meta['colors'] = available_colors

            yield Request(mini_item['url'], self.parse_colors, meta=meta)

    def parse_colors(self, response):
        available_colors = response.meta.get('colors', '')
        color_urls = response.css(
            '.product-swatches__list__usW6D a::attr(href)').getall()

        color_url_mapping = self.color_to_url_mapping(
            available_colors, color_urls)

        for color, urls in color_url_mapping.items():
            for url in urls:
                meta = deepcopy(response.meta)
                meta['item']['color'] = color
                url_to_parse = f'https://www.riverisland.com{url}'
                yield Request(url_to_parse, self.parse_detail, meta=meta)

    def color_to_url_mapping(self, available_colors, color_urls):
        color_url_mapping = {}
        for color in available_colors:
            color_url_mapping[color] = [
                url for url in color_urls if color.lower() in url.lower()]
        return color_url_mapping

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

    def parse_detail(self, response):
        item = response.meta.get('item')
        item['title'] = response.css(
            '.product-details__title__H5_jQ::text').get()
        item['base_sku'] = self.md5_hash(
            item['title'].replace(item['color'], ''))
        item['identifier'] = item['url'].split('-')[-1]
        item['price'] = response.css('.price__current-price::text').get()
        item['sizes'] = self.extract_size(response)
        item['url'] = response.url
        item['image_urls'] = response.css(
            '.carousel__image__BIe5r::attr(src)').getall()
        return item

    def extract_size(self, response):
        size_selector = '.product-details__size-select__ToWGJ li span.size-select__size__tusCt::text, .size-box__inner__Qz8SP::text'
        return response.css(size_selector).getall()

    def get_last_page(self, page_num_txt):
        numbers = self.PAGE_NUM_REGEX.findall(page_num_txt)
        return (int(numbers[0]) + 59) // 60 if numbers else None

    def parse_category(self, level):
        cat_txt = level.css('a::text').get().strip()
        cat_url = level.css('a::attr(href)').get()
        return cat_txt, cat_url

    @staticmethod
    def md5_hash(s, truncate=16):
        md5 = hashlib.md5(s.encode('utf-8')).hexdigest().upper()
        return md5[:truncate]

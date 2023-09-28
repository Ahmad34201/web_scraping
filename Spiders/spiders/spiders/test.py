import hashlib
import json
from copy import deepcopy

from scrapy import Request

from scrapyproduct.items import ProductItem, SizeItem
from scrapyproduct.spiderlib import SSBaseSpider
from scrapyproduct.toolbox import (category_mini_item, extract_text_nodes,
                                   update_query_params, parse_query_params, select_base_sku)


class MiintoDE(SSBaseSpider):

    de__countries_info = [
        # ('country', 'currency', 'language', 'url')
        ('fi', 'EUR', 'fi', 'https://www.miinto.fi/brands'),
        ('dk', 'DKK', 'da', 'https://www.miinto.dk/brands'),
        ('de', 'EUR', 'de', 'https://www.miinto.de/brands'),
        ('nl', 'EUR', 'nl', 'https://www.miinto.nl/brands'),
        ('no', 'NOK', 'no', 'https://www.miinto.no/brands'),
        ('se', 'SEK', 'sv', 'https://www.miinto.se/brands'),
        ('be', 'EUR', 'be', 'https://www.miinto.be/brands'),
        ('ch', 'CHF', 'de', 'https://www.miinto.ch/brands'),
        ('fr', 'EUR', 'fr', 'https://www.miinto.fr/brands'),
        ('gb', 'GBP', 'en', 'https://www.miinto.co.uk/brands'),
        ('it', 'EUR', 'it', 'https://www.miinto.it/brands'),
        ('pl', 'PLN', 'pl', 'https://www.showroom.pl/brands'),
    ]

    de__seen_identifier = {}
    de__desc_sel = '.p-product-page__description > div:not(.p-product-page__tabs-product-buttons)'
    de__exclude_desc = ['Versand & rückgabe', 'Livraison et retours', 'Verzending & retournering',
                        'Wysyłka i zwrot', 'Shipping & returns', 'Spedizione e resi', 'Frakt & retur'
                        'Verzending & retournering', 'Toimitus & palautus']
    de__pre_owned_keywords = ['pre-owned', 'preowned', 'pre owned', 'pre - owned', 'vintage']

    def start_requests(self):
        for country_code, currency, language, country_url in self.de__countries_info:
            if self.country and country_code not in self.country:
                continue

            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
                'dont_merge_cookies': True,
            }

            yield Request(country_url, self.de__parse_top_cats, meta=meta)

    def de__parse_top_cats(self, response):
        for level1 in response.css('.c-mm-v2-l1>li'):
            yield self.de__make_navigation_request(response, [level1])

            for level2 in level1.css('.c-mm-v2-l2>li'):
                yield self.de__make_navigation_request(response, [level1, level2])

                for level3 in level2.css('.c-mm-v2-l3__item'):
                    yield self.de__make_navigation_request(response, [level1, level2, level3])

                    for level4 in level3.css('.c-mm-v2-l4__item'):
                        yield self.de__make_navigation_request(response,
                                                               [level1, level2, level3, level4])

    def de__make_navigation_request(self, response, selectors):
        categories = [sel.css('a::text').get('').strip() for sel in selectors]
        if self.de__check_pre_owned_cat(categories):
            return
        url = selectors[-1].css('a::attr(href)').get()
        if not url:
            return
        meta = deepcopy(response.meta)
        meta['categories'] = categories
        meta['response_validation_func'] = self.validate_response
        return response.follow(url, self.de__parse_subcategories, meta=meta, dont_filter=True)

    def de__check_pre_owned_cat(self, categories):
        for cat in categories:
            cat_name = cat.lower()
            if 'pre-owned' in cat_name or 'vintage' in cat_name:
                return True
        return False

    @staticmethod
    def validate_response(request, response, spider):
        return bool(response.css('.c-product-card'))

    def de__parse_subcategories(self, response):
        sublinks = response.css('.p-category-tree__item.is-selected')
        if sublinks:
            for level5 in sublinks[-1].css('ul a'):
                url5 = level5.css('a::attr(href)').get()
                label5 = level5.css('a::text').get()
                meta = deepcopy(response.meta)
                meta['categories'] += [label5]
                callback = self.de__parse_subcategories if \
                    response.meta['country_code'] == 'ch' else self.de__parse_pagination
                yield response.follow(url5, callback, meta=meta)

        yield from self.de__parse_pagination(response)

    def de__parse_pagination(self, response):
        # yield products from current page
        yield from self.de__parse_products(response)

        last_page = response.css('.c-listing-pagination__link::attr(href)').getall()
        if not last_page:
            return
        total_pages = parse_query_params(last_page[-1])['page']
        for page in range(2, int(total_pages) + 1):
            params = {'page': page}
            url = update_query_params(response.url, params)
            yield Request(url, self.de__parse_products, meta=response.meta, dont_filter=True)

    def de__parse_products(self, response):
        for product in response.css('.c-product-card'):
            item = self.de__create_initial_item(response, product)
            yield category_mini_item(item)

            if self.are_only_mini_items_required():
                continue

            meta = deepcopy(response.meta)
            meta['item'] = item
            meta['response_validation_func'] = self.validate_detail
            yield Request(item['url'], self.de__parse_detail, meta=meta)

    def de__create_initial_item(self, response, sel_prod):
        identifier = sel_prod.attrib['data-product-id']
        return ProductItem(
            identifier=identifier,
            url=response.urljoin(sel_prod.attrib['data-product-url']),
            referer_url=response.url,
            category_names=response.meta['categories'],
            language_code=response.meta['language_code'],
            country_code=response.meta['country_code'],
            currency=response.meta['currency'],
        )

    def de__parse_detail(self, response):
        item = response.meta['item']
        item['title'] = self.de__get_title(response)
        item['brand'] = self.de__get_brand(response)
        if self.de__check_pre_owned(item['brand']) or self.de__check_pre_owned(item['title']):
            return
        item['base_sku'] = self.de__get_base_sku(response)
        item['description_text'] = self.de__get_description(response)
        item['color_name'], item['color_code'] = self.de__get_color(response)
        item['image_urls'] = self.de__get_images(response)
        item['size_infos'] = self.de__get_sizes(response)
        item['available'] = any(size['stock'] for size in item['size_infos'])
        return item

    def de__get_base_sku(self, sel):
        color_urls = sel.css('.js-color-selection a::attr(href)').getall() + [sel.url]
        color_ids = [self.md5_hash('-'.join(url.split('-')[-5:])) for url in color_urls]
        return select_base_sku(color_ids, self.de__seen_identifier)

    def de__get_title(self, sel):
        return sel.css('.p-product-page__product-name::text').get('').strip()

    def de__get_brand(self, sel):
        brand = sel.css('.p-product-page__product-brand::text').get('').strip()
        return brand or self.long_name

    def de__check_pre_owned(self, attr):
        attr_lower = attr.lower()
        if any([keyword for keyword in self.de__pre_owned_keywords if keyword in attr_lower]):
            return True
        return False

    def de__get_description(self, sel):
        description = []

        for desc in sel.css(self.de__desc_sel):
            title = desc.css('h3::text').get()
            if title in self.de__exclude_desc:
                continue
            description += extract_text_nodes(desc)

        return description or 'N/A'

    def de__get_color(self, sel):
        color_name = sel.css('[name="color"]::attr(value)').get('no_color').strip()
        return color_name, color_name

    def de__get_images(self, sel):
        return sel.css('.js-zoom-main-image-slide::attr(src)').getall()

    def de__get_sizes(self, sel):
        sizes = json.loads(sel.css('script:contains(ProductPage)').re_first('items: (.+)'))
        size_infos = []
        for size in sizes:
            old_price, new_price = self.de__get_price(size)
            size_infos.append(SizeItem(
                size_name=size['size'],
                size_identifier=size['miintoId'],
                stock=int(size['hasStock']),
                size_original_price_text=old_price,
                size_current_price_text=new_price
            ))
        return size_infos

    def de__get_price(self, size):
        def format_price(price):
            return str(price / 100.0)
        new_price = size['prices']['currentPrice']
        old_price = size['prices'].get('originalPrice') or new_price
        return format_price(old_price), format_price(new_price)

    @staticmethod
    def md5_hash(s, truncate=32):
        md5 = hashlib.md5(s.encode('utf-8')).hexdigest().upper()
        return md5[:truncate]

    @staticmethod
    def validate_detail(request, response, spider):
        return bool(response.css('.p-product-page__product-name'))


class MiintoSpider(MiintoDE):
    name = 'miinto'
    long_name = 'Miinto'
    version = '1.1.4'

    proxy_config = {
        '*': {'proxy_location': 'shader'},
    }

    TEST_SINGLE_ITEM = False
    TEST_SINGLE_CATEGORY = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.normalise_country()

    def start_requests(self):
        if self.TEST_SINGLE_ITEM:
            yield self.test_single_item()
            return

        if self.TEST_SINGLE_CATEGORY:
            yield self.test_category()
            return

        for base in self.__class__.__bases__:
            assert issubclass(base, SSBaseSpider)
            yield from base.start_requests(self)

    def test_single_item(self):
        url = 'Add_url'
        callback = self.de__parse_detail
        item = ProductItem(
            base_sku='test_sku',
            identifier='test_identifier',
            country_code='us',
            language_code='en',
            currency='USD',
            category_names=['Test cat'],
            url=url,
        )
        return Request(item['url'], callback, meta={'item': item})

    def test_category(self):
        category_url = 'Add_url'
        callback = self.de__parse_pagination
        meta = {
            'language_code': 'en',
            'currency': 'USD',
            'country_code': 'us',
            'categories': ['test'],
            'dont_merge_cookies': True,
            }
        return Request(category_url, callback, meta=meta)
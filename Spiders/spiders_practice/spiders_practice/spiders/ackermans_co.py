import json
import scrapy
from scrapy.loader import ItemLoader
from copy import deepcopy
from ..items import ProductItem, SizeItem, PriceItem, ProductLoader
from ..utils import *


class AckermanSpider(scrapy.Spider):
    de__countries_info = [
        # ('country', 'currency', 'language', 'url')
        ('gb', 'GBP', 'en', "https://www.ackermans.co.za/api/startup-data.jsonp?callback=handleStartupData"),
    ]
    name = 'ackerman_co'

    def start_requests(self):
        for country_code, currency, language, country_url in self.de__countries_info:

            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
            }

            yield scrapy.Request(country_url, self.de__parse_top_cats, meta=meta)

    def de__parse_top_cats(self, response):
        json_data = self.extract_json_data(response)
        if json_data:
            level1_cat = json_data.get('categories', [])[0]
            for cat1 in level1_cat.get('children', []):
                level1_cat_url = self.generate_level1_cat_url(
                    response.url, cat1.get('url_key', ''))
                yield from self.de__make_navigation_request(response, [cat1], level1_cat_url, cat1)

                for cat2 in cat1['children']:
                    level2_cat_url = f"{level1_cat_url}/{cat2.get('url_key', '')}"
                    yield from self.de__make_navigation_request(response, [cat1, cat2], level2_cat_url, cat2)

                    for cat3 in cat2['children']:
                        level3_cat_url = f"{level2_cat_url}/{cat3.get('url_key', '')}"
                        yield from self.de__make_navigation_request(response, [cat1, cat2, cat3], level3_cat_url, cat3)

                        for cat4 in cat3['children']:
                            level4_cat_url = f"{level3_cat_url}/{cat4.get('url_key', '')}"
                            yield from self.de__make_navigation_request(response, [cat1, cat2, cat3, cat4], level4_cat_url, cat4)

    def de__make_navigation_request(self, response, parent_categories, cat_url, category):
        if not category:
            return

        meta = deepcopy(response.meta)
        meta['cat_url'] = cat_url
        meta['cat_id'] = category.get('id','')
        meta['categories'] = [cat.get('name','') for cat in parent_categories]
        category_url = f"ack/products/{'/'.join(meta['categories'])}"
        PAGE_NUM_API = "https://www.ackermans.co.za/graphql?operationName=wpPages"
        yield scrapy.Request(PAGE_NUM_API, callback=self.de_make_pagination,
                             body=self.get_pages_payload(cat_url=category_url), method="POST", meta=meta,
                             headers=self.get_headers(cat_url=meta['cat_url']))

    def de_make_pagination(self, response):
        response_data = json.loads(response.text)
        total_page = response_data['data']['wpPages']['total']
        meta = deepcopy(response.meta)
        PRODUCT_API = "https://www.ackermans.co.za/graphql?operationName=products_listAndAggregations"
        for page_num in range(1, total_page+1):
            yield scrapy.Request(PRODUCT_API, callback=self.de__parse_products,
                                 body=self.get_payload(page_num, cat_id=meta['cat_id']), method="POST", meta=meta,
                                 headers=self.get_headers(cat_url=meta['cat_url']))

    def de__parse_products(self, response):
        response_data = json.loads(response.text)
        cat_url = response.meta.get('cat_url', '')
        if 'data' in response_data:
            data = response_data['data']
            if 'products' in data:
                products = data['products']
                if products is not None and 'items' in products:
                    items = products['items']
                    for response_item in items:
                        item_url = f"{cat_url}/{response_item['url_key']}"
                        item_id = response_item['id']
                        item = self.de__create_initial_item(
                            response, item_id, item_url)
                        yield item
                        yield from self.de__parse_detail(item, response_item, cat_url)

    def de__create_initial_item(self, response, identifier, url):
        categories = response.meta.get('categories', [])
        return ProductItem.create(response, identifier, url, categories)

    def de__parse_detail(self, item, response_item, cat_url):
        item['title'] = self.de__get_title(response_item)
        item['description'] = self.de__get_description(response_item)
        item['base_sku'] = self.de__get_base_sku(response_item)
        item['price'] = self.get_price(response_item)
        item['image_urls'] = self.get_image_urls(response_item)
        item['availability'] = self.check_availability(response_item)

        yield scrapy.Request(
            "https://www.ackermans.co.za/graphql?operationName=products_pdp",
            callback=self.de__get_sizes,
            body=self.get_sizes_payload(response_item['url_key']),
            method="POST",
            headers=self.get_headers(cat_url=cat_url),
            meta={'item': item}
        )

    def de__get_sizes(self, response):
        sizes = []
        response_data = json.loads(response.text)
        if 'data' in response_data:
            for item in response_data['data']['products']['items']:
                for variant in item['variants']:
                    identifier = self.de__get_identifier(variant['product'])
                    price = self.get_price(variant['product'])
                    availability = self.check_availability(variant['product'])
                    size = variant['attributes'][1]['label'].strip()
                    sizes.append(SizeItem.create(
                        identifier, size, availability, price))
        meta = deepcopy(response.meta)
        item = meta['item']
        item['sizes'] = sizes
        return item

    def de__get_title(self, item):
        return item['name']

    def de__get_description(self, item):
        return item['meta_description']

    def de__get_base_sku(self, item):
        return item['sku']

    def de__get_identifier(self, item):
        return item['id']

    def check_availability(self, item):
        status = item['stock_status']
        return 1 if status == "IN_STOCK" else 0

    def get_price(self, item):
        price = item['price_range']['minimum_price']
        actual_price = price['regular_price'].get('value', '')
        final_price = price['final_price'].get('value', '')
        return PriceItem.create(actual_price, final_price)

    def get_image_urls(self, item):
        return [
            f'https://www.ackermans.co.za/imagekit/olyekz3oue/prod-ack-product-images/{image["file_name"]}.png?tr=w-1100,h-auto,bg-FFFFFF,f-webp,dpr-1'
            for image in item['media_gallery']
        ]

    def extract_json_data(self, response):
        pattern = r'handleStartupData\((.*?)\)'
        match = re.search(pattern, response.text)

        if match:
            json_data = match.group(1)
            try:
                return json.loads(json_data)
            except json.JSONDecodeError as e:
                self.logger.error(f"Error decoding JSON data: {e}")
        else:
            self.logger.error("No JSON data found in the response text")
            return None

    def generate_level1_cat_url(self, base_url, level1_cat_url_key):
        return urljoin(base_url, urljoin("/products/", level1_cat_url_key))

    def get_payload(self, page_num, cat_id):
        payload = json.dumps({
            "operationName": "products_listAndAggregations",
            "variables": {},
            "query": f"query products_listAndAggregations {{\n  products(\n    filter: {{category_id: {{eq: \"{cat_id}\"}}}}\n    search: \"\"\n    sort: {{}}\n    pageSize: 20\n    currentPage: {page_num}\n  ) {{\n    items {{\n      __typename\n      id\n      sku\n      stock_status\n      name\n      description {{\n        html\n        __typename\n      }}\n      product_attribute\n      product_decal\n      media_gallery {{\n        file_name\n        label\n        position\n        disabled\n        __typename\n      }}\n      price_range {{\n        minimum_price {{\n          ...AllPriceFields\n          __typename\n        }}\n        __typename\n      }}\n      url_key\n      meta_title\n      meta_description\n      categories {{\n        id\n        __typename\n      }}\n    }}\n    total_count\n    aggregations(filter: {{category: {{includeDirectChildrenOnly: true}}}}) {{\n      attribute_code\n      count\n      label\n      options {{\n        count\n        label\n        value\n        __typename\n      }}\n      __typename\n    }}\n    sort_fields {{\n      default\n      options {{\n        label\n        value\n        __typename\n      }}\n      __typename\n    }}\n    __typename\n  }}\n}}\n\nfragment AllPriceFields on ProductPrice {{\n  final_price {{\n    value\n    __typename\n  }}\n  regular_price {{\n    value\n    __typename\n  }}\n  __typename\n}}\n"
        })
        return payload

    def get_headers(self, cat_url):
        headers = {
            'authority': 'www.ackermans.co.za',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'cookie': '_gcl_au=1.1.401444600.1695297098; _gid=GA1.3.256424764.1695297098; _fbp=fb.2.1695297099975.1441491622; cebs=1; _tt_enable_cookie=1; _ttp=H0B_g8QO3kOfYQFA4OHQptAjUPY; _ce.clock_event=1; _ce.clock_data=-616%2C110.39.173.34%2C1%2C84fb6a68ab92a6d30981c69a1117885c; _ga=GA1.1.1448215736.1695297098; cebsp_=43; _ga_VH8M4TS2RY=GS1.1.1695375550.8.1.1695375818.60.0.0; _ga_FEHGW0VZ85=GS1.1.1695375551.6.1.1695375818.60.0.0; _ce.s=v~694b4e37cdb0b0ae52759a4c858285beb174219e~lcw~1695376029281~vpv~0~v11.fhb~1695375552415~v11.lhb~1695376091020~ir~1~gtrk.la~lmtaocor~lcw~1695376091021',
            'origin': 'https://www.ackermans.co.za',
            'pragma': 'no-cache',
            'referer': {cat_url},
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
        }
        return headers

    def get_pages_payload(self, cat_url):
        page_nums_payload = json.dumps({
            "operationName": "wpPages",
            "variables": {
                "facade_url_tree": cat_url,
                "status": "publish"
            },
            "query": "query wpPages($facade_url_tree: String, $status: String, $page: String, $per_page: String, $facade_parent_include_level: Int, $include: String) {\n  wpPages(\n    facade_url_tree: $facade_url_tree\n    status: $status\n    page: $page\n    per_page: $per_page\n    facade_parent_include_level: $facade_parent_include_level\n    include: $include\n  ) {\n    total\n    totalPages\n    items {\n      id\n      title {\n        rendered\n        __typename\n      }\n      slug\n      parent\n      link\n      template\n      acf\n      __typename\n    }\n    __typename\n  }\n}\n"
        })
        return page_nums_payload

    def get_sizes_payload(self, url_key):
        payload = json.dumps({
            "operationName": "products_pdp",
            "variables": {
                "urlKey": url_key
            },
            "query": "query products_pdp($urlKey: String) {\n  products(filter: {url_key: {eq: $urlKey}}) {\n    items {\n      __typename\n      id\n      sku\n      name\n      description {\n        html\n        __typename\n      }\n      price_range {\n        minimum_price {\n          ...AllPriceFields\n          __typename\n        }\n        __typename\n      }\n      url_key\n      meta_title\n      meta_description\n      stock_status\n      product_attribute\n      product_decal\n      categories {\n        id\n        name\n        url_path\n        __typename\n      }\n      related_products {\n        sku\n        __typename\n      }\n      media_gallery {\n        file_name\n        label\n        position\n        disabled\n        __typename\n      }\n      size_guide\n      washcare_guide\n      manufacturer\n      product_attribute\n      product_decal\n      colour\n      gender\n      pim_product_category\n      pim_size_guide\n      pim_wash_care_guide\n      primarycolour\n      productsize\n      sizesortseq\n      ... on ConfigurableProduct {\n        variants {\n          product {\n            id\n            sku\n            price_range {\n              minimum_price {\n                ...AllPriceFields\n                __typename\n              }\n              __typename\n            }\n            stock_status\n            sizesortseq\n            __typename\n          }\n          attributes {\n            label\n            code\n            value_index\n            uid\n            __typename\n          }\n          __typename\n        }\n        __typename\n      }\n    }\n    __typename\n  }\n}\n\nfragment AllPriceFields on ProductPrice {\n  discount {\n    ...ProductDiscountFields\n    __typename\n  }\n  final_price {\n    ...MoneyFields\n    __typename\n  }\n  regular_price {\n    ...MoneyFields\n    __typename\n  }\n  __typename\n}\n\nfragment ProductDiscountFields on ProductDiscount {\n  amount_off\n  percent_off\n  __typename\n}\n\nfragment MoneyFields on Money {\n  value\n  __typename\n}\n"
        })
        return payload

import json
from copy import deepcopy

from scrapy import Request, Spider

from ..items import ProductItem, SizeItem, PriceItem
from ..utils import *


class AckermanSpider(Spider):
    de__countries_info = [
        # ('country', 'currency', 'language', 'url')
        ('gb', 'GBP', 'en', "https://www.ackermans.co.za/api/startup-data.jsonp?callback=handleStartupData"),
    ]
    name = 'ackerman_co'
    PAGE_NUM_API = "https://www.ackermans.co.za/graphql?operationName=wpPages"
    PRODUCT_API = "https://www.ackermans.co.za/graphql?operationName=products_listAndAggregations"

    def start_requests(self):
        for country_code, currency, language, country_url in self.de__countries_info:

            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
            }

            yield Request(country_url, self.de__parse_top_cats, meta=meta)

    def de__parse_top_cats(self, response):
        json_data = self.extract_json_data(response)
        if json_data:
            level1_cat = json_data.get('categories', [])[0]
            for cat1 in level1_cat.get('children', []):
                cat1_url = self.generate_level1_cat_url(
                    response.url, cat1.get('url_key', ''))
                yield from self.de__make_navigation_request(response, [], cat1_url, cat1)

                for cat2 in cat1['children']:
                    cat2_url = f"{cat1_url}/{cat2.get('url_key', '')}"
                    yield from self.de__make_navigation_request(response, [cat1], cat2_url, cat2)

                    for cat3 in cat2['children']:
                        cat3_url = f"{cat2_url}/{cat3.get('url_key', '')}"
                        yield from self.de__make_navigation_request(response, [cat1, cat2], cat3_url, cat3)

                        for cat4 in cat3['children']:
                            cat4_url = f"{cat3_url}/{cat4.get('url_key', '')}"
                            yield from self.de__make_navigation_request(response, [cat1, cat2, cat3], cat4_url, cat4)

    def de__make_navigation_request(self, response, parent_categories, cat_url, current_category):
        if not current_category:
            return

        meta = deepcopy(response.meta)
        meta['cat_url'] = cat_url
        meta['cat_id'] = current_category.get('id', '')
        meta['categories'] = [cat.get('name', '')
                              for cat in parent_categories + [current_category]]
        category_url = f"ack/products/{'/'.join(meta['categories'])}"

        yield Request(
            url=self.PAGE_NUM_API,
            callback=self.de_make_pagination,
            body=self.get_pages_payload(cat_url=category_url),
            method="POST",
            meta=meta,
            headers=self.get_headers(cat_url=meta['cat_url'])
        )

    def de_make_pagination(self, response):
        response_data = json.loads(response.text)
        total_page = response_data['data']['wpPages']['total']
        meta = deepcopy(response.meta)

        for page_num in range(1, total_page+1):
            yield Request(self.PRODUCT_API, callback=self.de__parse_products,
                          body=self.get_payload(page_num, cat_id=meta['cat_id']), method="POST", meta=meta,
                          headers=self.get_headers(cat_url=meta['cat_url']))

    def de__parse_products(self, response):
        response_data = json.loads(response.text)
        cat_url = response.meta.get('cat_url', '')
        yield from self.process_response_data(response, cat_url, response_data)

    def de__create_initial_item(self, response, identifier, url):
        categories = response.meta.get('categories', [])
        return ProductItem(
            identifier=identifier,
            url=url,
            category_names=categories,
            country_code=response.meta.get('country_code', ''),
            language_code=response.meta.get('language_code', ''),
            currency=response.meta.get('currency', '')
        )

    def process_response_data(self, response, cat_url, response_data):
        if 'data' in response_data:
            data = response_data['data']
            if 'products' in data:
                products = data['products']
                if products is not None and 'items' in products:
                    items = products['items']
                    for response_item in items:
                        yield from self.process_item(response, cat_url, response_item)

    def process_item(self, response, cat_url, response_item):
        item_url = f"{cat_url}/{response_item['url_key']}"
        item_id = response_item['id']
        mini_item = self.de__create_initial_item(response, item_id, item_url)
        yield mini_item
        yield from self.de__parse_detail(mini_item, response_item, cat_url)

    def de__parse_detail(self, item, response_item, cat_url):
        item['title'] = response_item['name']
        item['description'] = response_item['meta_description']
        item['base_sku'] = response_item['sku']
        item['price'] = self.get_price(response_item)
        item['image_urls'] = self.get_image_urls(response_item)
        item['availability'] = self.check_availability(response_item)

        yield Request(
            "https://www.ackermans.co.za/graphql?operationName=products_pdp",
            callback=self.de__get_sizes,
            body=self.get_sizes_payload(response_item['url_key']),
            method="POST",
            headers=self.get_headers(cat_url=cat_url),
            meta={'item': item}
        )

    def extract_size_data(self, variant):
        identifier = variant['product']['id']
        price = self.get_price(variant['product'])
        availability = self.check_availability(variant['product'])
        size = variant['attributes'][1]['label'].strip()
        return identifier, size, availability, price

    def create_size_items(self, response_data):
        sizes = []
        if 'data' in response_data:
            for item in response_data['data']['products']['items']:
                for variant in item['variants']:
                    identifier, size, availability, price = self.extract_size_data(
                        variant)
                    sizes.append(SizeItem(
                        identifier=identifier,
                        producerSize=size,
                        stock=availability,
                        price=price))
        return sizes

    def update_item_with_sizes(self, meta, sizes):
        item = meta['item']
        item['sizes'] = sizes
        return item

    def de__get_sizes(self, response):
        response_data = json.loads(response.text)
        sizes = self.create_size_items(response_data)
        meta = deepcopy(response.meta)
        return self.update_item_with_sizes(meta, sizes)

    def check_availability(self, item):
        status = item['stock_status']
        return 1 if status == "IN_STOCK" else 0

    def get_price(self, item):
        price = item['price_range']['minimum_price']
        actual_price = price['regular_price'].get('value', '')
        final_price = price['final_price'].get('value', '')
        return PriceItem(
            original=actual_price,
            final=final_price,
        )

    def get_image_urls(self, item):
        return [
            (
                f'https://www.ackermans.co.za/imagekit/olyekz3oue/prod-ack-product-images/'
                f'{image["file_name"]}.png?tr=w-1100,h-auto,bg-FFFFFF,f-webp,dpr-1'
            )
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
            "query": """
                query products_listAndAggregations {
                products(
                    filter: {category_id: {eq: "%s"}}
                    search: ""
                    sort: {}
                    pageSize: 20
                    currentPage: %s
                ) {
                    items {
                    __typename
                    id
                    sku
                    stock_status
                    name
                    description {
                        html
                        __typename
                    }
                    product_attribute
                    product_decal
                    media_gallery {
                        file_name
                        label
                        position
                        disabled
                        __typename
                    }
                    price_range {
                        minimum_price {
                        ...AllPriceFields
                        __typename
                        }
                        __typename
                    }
                    url_key
                    meta_title
                    meta_description
                    categories {
                        id
                        __typename
                    }
                    }
                    total_count
                    aggregations(filter: {category: {includeDirectChildrenOnly: true}}) {
                    attribute_code
                    count
                    label
                    options {
                        count
                        label
                        value
                        __typename
                    }
                    __typename
                    }
                    sort_fields {
                    default
                    options {
                        label
                        value
                        __typename
                    }
                    __typename
                    }
                    __typename
                }
                }

                fragment AllPriceFields on ProductPrice {
                final_price {
                    value
                    __typename
                }
                regular_price {
                    value
                    __typename
                }
                __typename
                }
            """ % (cat_id, page_num)
        })
        return payload

    def get_headers(self, cat_url):
        headers = {
            'authority': 'www.ackermans.co.za',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'no-cache',
            'content-type': 'application/json',
            'cookie': ('_gcl_au=1.1.401444600.1695297098; '
                       '_gid=GA1.3.256424764.1695297098; '
                       '_fbp=fb.2.1695297099975.1441491622; cebs=1; '
                       '_tt_enable_cookie=1; _ttp=H0B_g8QO3kOfYQFA4OHQptAjUPY; '
                       '_ce.clock_event=1; '
                       '_ce.clock_data=-616%2C110.39.173.34%2C1%2C84fb6a68ab92a6d30981c69a1117885c; '
                       '_ga=GA1.1.1448215736.1695297098; cebsp_=43; '
                       '_ga_VH8M4TS2RY=GS1.1.1695375550.8.1.1695375818.60.0.0; '
                       '_ga_FEHGW0VZ85=GS1.1.1695375551.6.1.1695375818.60.0.0; '
                       '_ce.s=v~694b4e37cdb0b0ae52759a4c858285beb174219e~lcw~1695376029281~vpv~0~v11.fhb~1695375552415~v11.lhb~1695376091020~ir~1~gtrk.la~lmtaocor~lcw~1695376091021'),
            'origin': 'https://www.ackermans.co.za',
            'pragma': 'no-cache',
            'referer': cat_url,
            'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
                           '(KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36')
        }
        return headers

    def get_pages_payload(self, cat_url):
        page_nums_payload = json.dumps({
            "operationName": "wpPages",
            "variables": {
                "facade_url_tree": cat_url,
                "status": "publish"
            },
            "query": """
            query wpPages($facade_url_tree: String, $status: String, $page: String, $per_page: String, $facade_parent_include_level: Int, $include: String) {
                wpPages(
                    facade_url_tree: $facade_url_tree
                    status: $status
                    page: $page
                    per_page: $per_page
                    facade_parent_include_level: $facade_parent_include_level
                    include: $include
                ) {
                    total
                    totalPages
                    items {
                        id
                        title {
                            rendered
                            __typename
                        }
                        slug
                        parent
                        link
                        template
                        acf
                        __typename
                    }
                    __typename
                }
            }
            """
        })
        return page_nums_payload

    def get_sizes_payload(self, url_key):
        payload = json.dumps({
            "operationName": "products_pdp",
            "variables": {
                "urlKey": url_key
            },
            "query": """
            query products_pdp($urlKey: String) {
                products(filter: {url_key: {eq: $urlKey}}) {
                    items {
                        __typename
                        id
                        sku
                        name
                        description {
                            html
                            __typename
                        }
                        price_range {
                            minimum_price {
                                ...AllPriceFields
                                __typename
                            }
                            __typename
                        }
                        url_key
                        meta_title
                        meta_description
                        stock_status
                        product_attribute
                        product_decal
                        categories {
                            id
                            name
                            url_path
                            __typename
                        }
                        related_products {
                            sku
                            __typename
                        }
                        media_gallery {
                            file_name
                            label
                            position
                            disabled
                            __typename
                        }
                        size_guide
                        washcare_guide
                        manufacturer
                        product_attribute
                        product_decal
                        colour
                        gender
                        pim_product_category
                        pim_size_guide
                        pim_wash_care_guide
                        primarycolour
                        productsize
                        sizesortseq
                        ... on ConfigurableProduct {
                            variants {
                                product {
                                    id
                                    sku
                                    price_range {
                                        minimum_price {
                                            ...AllPriceFields
                                            __typename
                                        }
                                        __typename
                                    }
                                    stock_status
                                    sizesortseq
                                    __typename
                                }
                                attributes {
                                    label
                                    code
                                    value_index
                                    uid
                                    __typename
                                }
                                __typename
                            }
                            __typename
                        }
                    }
                    __typename
                }
            }

            fragment AllPriceFields on ProductPrice {
                discount {
                    ...ProductDiscountFields
                    __typename
                }
                final_price {
                    ...MoneyFields
                    __typename
                }
                regular_price {
                    ...MoneyFields
                    __typename
                }
                __typename
            }

            fragment ProductDiscountFields on ProductDiscount {
                amount_off
                percent_off
                __typename
            }

            fragment MoneyFields on Money {
                value
                __typename
            }
            """
        })
        return payload

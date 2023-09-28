import json
import scrapy
from urllib.parse import urljoin
from ..items import ProductItem
from urllib.parse import urlparse
from operator import itemgetter
from ..utils import *

class BeyondYogaSpider(scrapy.Spider):
    name = 'beyond_yoga'
    start_urls = ['https://beyondyoga.com/']
    custom_settings = {
        'FEEDS': {'data.jsonl': {'format': 'jsonlines'}}
    }

    def parse(self, response):
        # Extract sub-category links and initiate parsing of detailed pages
        main_categories = response.xpath(
            '//li[contains(@class, "site-header-nav__item")]')
        for main_category in main_categories:
            sub_category_links = main_category.xpath(
                './/div[contains(@class, "site-header-nav-mega-menu__child-link")]/a/@href').getall()
            for sub_category_link in sub_category_links:
                abs_link = get_absolute_url(
                    response.url, sub_category_link)
                yield scrapy.Request(abs_link, callback=self.parse_detailed_page)
                break
            break

    def parse_detailed_page(self, response):
        # Extract product links from detailed page and initiate parsing of product pages
        product_items = response.xpath(
            '//li[contains(@class, "collection-grid__grid-item")]')
        for product_item in product_items:
            detailed_link = urljoin(response.url, product_item.xpath(
                './/a[contains(@class, "product-card__info-wrapper")]/@href').get())
            yield scrapy.Request(detailed_link, callback=self.parse_product)

    def parse_product(self, response):
        # Extract product info and initiate parsing of color pages
        product, seasonal_url, core_url = self.extract_product_info(response)
        yield scrapy.Request(core_url, callback=self.extract_core_colors, cb_kwargs={'product': product, 'seasonal_url': seasonal_url})

    def extract_product_info(self, response):
        # Extract general product info and color URLs
        product = ProductItem()
        identifier = extract_text(
            response, './/script[contains(@id, "ActiveVariantJSON")]')
        product['identifier'] = json.loads(identifier).get('id', None)
        product['product_url'] = response.url
        product['title'] = extract_text(
            response, '//h1[contains(@class, "product__title")]')
        product['price'] = extract_text(
            response, './/div[contains(@class, "product__price")]')

        image_urls = extract_attributes(
            response, '//div[contains(@class, "product-images__img")]//img', 'src')
        normalized_image_urls = [normalize_url(
            response, url) for url in image_urls]
        product['image_urls'] = normalized_image_urls
        product['description'] = self.extract_description(
            response, '//div[contains(@class, "product__description")]')

        # Compose URLs for color pages
        core_url = self.compose_colors_url(response, "core")
        seasonal_url = self.compose_colors_url(response, "seasonal")
        return product, seasonal_url, core_url

    def extract_core_colors(self, response, product, seasonal_url):
        # Extract core colors and initiate parsing of seasonal color page
        script_content = response.xpath(
            '//script[@type="text/javascript"]/text()').get()
        updated_product = self.update_product_colors(
            script_content, product, 'core_colors')
        yield scrapy.Request(seasonal_url, callback=self.extract_seasonal_colors, cb_kwargs={'product': updated_product})

    def extract_seasonal_colors(self, response, product):
        # Extract seasonal colors and yield the updated product
        script_content = response.xpath(
            '//script[@type="text/javascript"]/text()').get()
        updated_product = self.update_product_colors(
            script_content, product, 'seasonal_colors')
        yield updated_product

    def extract_description(self, response, xpath_expr):
        # Extract and preprocess product description
        text_nodes = response.xpath(f'{xpath_expr}//text()').getall()
        cleaned_text = ' '.join([normalize_space(node)
                                for node in text_nodes])
        cleaned_text = preprocess_text(cleaned_text)
        return cleaned_text.strip() if cleaned_text else None

    def compose_colors_url(self, response, color_type):
        # Compose URL for color pages based on color type
        parsed_url = urlparse(response.url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        data = response.xpath(
            f'//div[contains(@class, "product__related-colors-{color_type}")]/@data-{color_type}').get()
        data_group = response.xpath(
            f'//div[contains(@class, "product__related-colors-{color_type}")]/@data-group').get()
        url = urljoin(
            base_url, f"collections/{data}/{data_group}?view=json")
        return url

    def update_product_colors(self, script_content, product, color_type):
        # Update product colors with extracted data
        data = json.loads(script_content)
        colors = list(map(itemgetter('color'), data))
        available_sizes = list(map(itemgetter('options'), data))
        color_to_sizes_mapping = dict(zip(colors, available_sizes))
        product[color_type] = color_to_sizes_mapping
        return product

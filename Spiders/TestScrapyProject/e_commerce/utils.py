import re
from urllib.parse import urljoin

def strip_if_not_none(text):
    return text.strip() if text is not None else ""

def extract_text(response, xpath_expr):
    text = response.xpath(f'{xpath_expr}/text()').get()
    return text.strip() if text else None

def extract_attributes(response, xpath_expr, attr_name):
    return response.xpath(f'{xpath_expr}/@{attr_name}').getall()

def normalize_space(text):
    return ' '.join(text.strip().split())

def preprocess_text(text):
    # Remove HTML comments
    text = re.sub(r'<!--(.*?)-->', '', text)
    # Remove style declarations
    text = re.sub(r'<style.*?>.*?</style>', '', text)
    return text.strip()

def normalize_url(response, url):
    return urljoin(response.url, url.strip())

def get_absolute_url(base_url, rel_url):
    if rel_url.startswith('/'):
        return urljoin(base_url, rel_url)
    return rel_url


def extract_product_url(response):
    return response.url



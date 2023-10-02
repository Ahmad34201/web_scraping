import json
from copy import deepcopy

from scrapy import Request, Spider

from ..items import ProductItem, SizeItem, PriceItem
from ..utils import *


class HeavenSpider(Spider):
    de__countries_info = [
        # ('country', 'currency', 'language', 'url')
        ('gb', 'GBP', 'en', "https://www.marcjacobs.com/default/the-marc-jacobs/bags/view-all-bags-1/"),
    ]
    name = 'heaven'
    headers = {
        'authority': 'www.marcjacobs.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        # 'cookie': 'dwac_1b8b4169444398a5bd71b5531a=Fc2HHn6ryd0F2yddd33R8PhugkpG-uZK4mU%3D|dw-only|||USD|false|US%2FEastern|true; cqcid=acy6tT44QkDhlaIwmoPKMs4TlH; cquid=||; sid=Fc2HHn6ryd0F2yddd33R8PhugkpG-uZK4mU; GlobalE_Data=%7B%22countryISO%22%3A%22NL%22%2C%22cultureCode%22%3A%22nl-NL%22%2C%22currencyCode%22%3A%22EUR%22%2C%22apiVersion%22%3A%222.1.4%22%7D; dwanonymous_925c5c911dedc4dc1a345433a8c82587=acy6tT44QkDhlaIwmoPKMs4TlH; __cq_dnt=0; dw_dnt=0; dwsid=ikVKFlU_WLS-GXFCgUmqi2fmT0JtbncjWafERymkD_Tloqv8N9cnaajPdLtDGk8wy9FZMFi1dBHqBZ3tAvMHfg==; nostojs=autoload; 2c.cId=651548482f14d5413e43319b; __cq_uuid=acy6tT44QkDhlaIwmoPKMs4TlH; __cq_seg=0~0.00!1~0.00!2~0.00!3~0.00!4~0.00!5~0.00!6~0.00!7~0.00!8~0.00!9~0.00; liveagent_oref=; GlobalE_Welcome_Data=%7B%22showWelcome%22%3Afalse%7D; liveagent_sid=5d361fa0-e149-4940-bcd4-005a61c6ccf8; liveagent_vc=2; liveagent_ptid=5d361fa0-e149-4940-bcd4-005a61c6ccf8; GlobalE_Full_Redirect=false; OptanonAlertBoxClosed=2023-09-28T09:34:07.058Z; _gid=GA1.2.1474409413.1695893648; _gcl_au=1.1.1560200806.1695893649; _scid=a45ba716-35ea-46b2-988d-dc0dacdb4a97; _tt_enable_cookie=1; _ttp=khhwPvQ9uCvbgflMgj2cc71CtRP; _fbp=fb.1.1695893652898.1323546889; __qca=P0-1525405791-1695893651645; __attentive_id=fc63fa4a7acd457b9226372f5b2e75ec; _attn_=eyJ1Ijoie1wiY29cIjoxNjk1ODkzNjU1OTYyLFwidW9cIjoxNjk1ODkzNjU1OTYyLFwibWFcIjoyMTkwMCxcImluXCI6ZmFsc2UsXCJ2YWxcIjpcImZjNjNmYTRhN2FjZDQ1N2I5MjI2MzcyZjViMmU3NWVjXCJ9In0=; __attentive_cco=1695893655966; __attentive_dv=1; tangiblee:widget:user=78875940-be6b-4ae8-8dec-28ded4526d73; __cq_bc=%7B%22aaqt-marcjacobs%22%3A%5B%7B%22id%22%3A%222F3HCR045H01%22%2C%22sku%22%3A%22196611092463%22%7D%2C%7B%22id%22%3A%22H009L01SP21%22%2C%22sku%22%3A%22196611039505%22%7D%5D%7D; _ga_90JWNMS35B=GS1.1.1695897660.1.0.1695897661.0.0.0; _ga_tng=GA1.3.78875940-be6b-4ae8-8dec-28ded4526d73; _ga_tng_gid=GA1.3.2020232654.1695897668; _conv_v=vi%3A1*sc%3A1*cs%3A1695897661*fs%3A1695897661*pv%3A1*exp%3A%7B100421225.%7Bv.100457048-g.%7B100412916.1%7D%7D%7D; _sctr=1%7C1695841200000; _gat__ga=1; ABTastySession=mrasn=&lp=https%253A%252F%252Fwww.marcjacobs.com%252F; ABTasty=uid=1trkka31gewxzcw6&fst=1695893570588&pst=1695893570588&cst=1695906916519&ns=2&pvt=26&pvis=3&th=1074727.1333650.7.7.1.1.1695893573438.1695896291680.1.1; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Sep+28+2023+18%3A48%3A39+GMT%2B0500+(Pakistan+Standard+Time)&version=202308.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=de60deb0-ee96-43d1-ac71-d5ad6639d696&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1&geolocation=NL%3BNH&AwaitingReconsent=false; GlobalE_CT_Data=%7B%22CUID%22%3A%22602633756.747584423.494%22%2C%22CHKCUID%22%3Anull%2C%22GA4SID%22%3A708167850%2C%22GA4TS%22%3A1695908919690%7D; _ga=GA1.1.910992947.1695893648; _scid_r=a45ba716-35ea-46b2-988d-dc0dacdb4a97; _uetsid=2e9bb0305de211ee981885e80367d236; _uetvid=2e9c26905de211ee850de578e844aadb; __attentive_pv=3; __attentive_ss_referrer=https://www.marcjacobs.com/default/the-marc-jacobs/bags/view-all-bags-1/; _ga_QLHB95L78F=GS1.1.1695906913.2.1.1695908925.0.0.0; GlobalE_Data=%7B%22countryISO%22%3A%22US%22%2C%22cultureCode%22%3A%22en-US%22%2C%22currencyCode%22%3A%22USD%22%2C%22apiVersion%22%3A%222.1.4%22%7D; __cq_dnt=0; cqcid=bd3S0Ugc1fQgpRbmoEkp1SacAw; cquid=||; dw_dnt=0; dwac_1b8b4169444398a5bd71b5531a=hT63oYMLiC9zaScr3slFJL6iae3c9wsXGbQ%3D|dw-only|||USD|false|US%2FEastern|true; dwanonymous_925c5c911dedc4dc1a345433a8c82587=bd3S0Ugc1fQgpRbmoEkp1SacAw; dwsid=Sy9t2Q3UYMfDbN5hmw1MqnCzs5VSKOP_qbEzlDluAg-01jujPgKn5r8jOXd2gfN0Dq2OH1giqOpvyC7qFab_KQ==; sid=hT63oYMLiC9zaScr3slFJL6iae3c9wsXGbQ',
        'pragma': 'no-cache',
        'referer': 'https://www.marcjacobs.com/default/the-marc-jacobs/bags/view-all-bags-1/',
        'sec-ch-ua': '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }

    def start_requests(self):
        for country_code, currency, language, country_url in self.de__countries_info:

            meta = {
                'language_code': language,
                'currency': currency,
                'country_code': country_code,
            }
            print("url", country_url)
            yield Request(country_url, callback=self.de__parse_top_cats, headers=self.headers)

    def de__parse_top_cats(self, response):
        print("called.... ")
        for level1 in response.xpath('//div[@class="nav-modal__main-list-item"]'):
            pass

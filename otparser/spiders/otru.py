import scrapy
from scrapy.http import HtmlResponse
from otparser.items import OtparserItem
from scrapy.loader import ItemLoader

class OtruSpider(scrapy.Spider):
    name = 'otru'
    allowed_domains = ['onlinetrade.ru']
    url = 'http://onlinetrade.ru'

    def __init__(self, search):
        super(OtruSpider, self).__init__()
        self.start_urls = [f'https://onlinetrade.ru/sitesearch.html?query={search}']

    def parse(self, response: HtmlResponse):
        goods_links = response.xpath("//a[@class='indexGoods__item__image']")
        for link in goods_links:
            yield response.follow(link, callback=self.parse_good)

        price_list = response.xpath("//span[@class='price regular']/text()")
        for price in price_list:
            price = int(''.join(i for i in price.extract() if i in '1234567890'))
            # Как передать price в item?

        next_page = response.xpath("//a[contains(@title, 'Следующие')]/@href").extract()[0]
        if next_page:
            next_page = self.url + next_page
            yield response.follow(next_page, callback=self.parse)

    def parse_good(self, response: HtmlResponse):
        loader = ItemLoader(item=OtparserItem(), response=response)

        loader.add_xpath('name', "//h1/text()")
        loader.add_xpath('photo', "//img[@class='displayedItem__images__thumbImage']/@src")
        loader.add_xpath('params', "//li[@class ='featureList__item']/span/text() | \
                                    //li[@class ='featureList__item']/text()")
        loader.add_value('link', response.url)

        loader.add_xpath('price', "//span[@class='js__actualPrice']/text()")
        # не передает цену, выводит 'price': [' ₽']
        # пробовал собрать через страницу поиска, там получается
        # но я не знаю как прикрепить ее к item_у

        yield loader.load_item()

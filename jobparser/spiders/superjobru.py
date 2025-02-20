import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import Jobparser


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=Python']

    def parse(self, response: HtmlResponse):  # в response передается start_urls и делается get-запрос
        next_page = response.xpath("//span[text()='Дальше']/@href").extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

        vacancies_links = response.xpath("//div[contains(@class, '_21a7u')]/a/@href").extract()  # список вакансий
        for link in vacancies_links:  # обходим весь список
            yield response.follow(link, callback=self.vacancy_parse)  # создает новый get-запрос по указаной ссылки и
                                                                      # ответ передает в указанный метод

    def vacancy_parse(self, response: HtmlResponse):
        item_name = response.xpath("//h1/text()").extract_first()
        item_salary = response.xpath("//span[@class='_1h3Zg _2Wp8I _2rfUm _2hCDz']/text()").extract()
        item_link = response.url

        item = Jobparser(name=item_name, salary=item_salary, link=item_link, website='superjob.ru')
        yield item

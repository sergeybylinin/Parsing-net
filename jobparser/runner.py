# Файл runner.py не обязательный. Создан для отлеживания работы проекта
# Повторяет логику scrapy

from scrapy.crawler import CrawlerProcess                   # импорт базового класса
from scrapy.settings import Settings                        # импорт глобальных настроек

from jobparser import settings                              # импорт наших настроек
from jobparser.spiders.hhru import HhruSpider               # импорт класса паука hh.ru
from jobparser.spiders.superjobru import SjruSpider

if __name__ == '__main__':
    crawler_settings = Settings()                           # Создание объекта настроек
    crawler_settings.setmodule(settings)                    # Загрузка наших настроек

    process = CrawlerProcess(settings=crawler_settings)     # Создание процесса парсига
    process.crawl(HhruSpider)                               # "Найм" паука hh.ru
    process.crawl(SjruSpider)                               # "Найм" паука superjob.ru

    process.start()                                         # Запуск процесса


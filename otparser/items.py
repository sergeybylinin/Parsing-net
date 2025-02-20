# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, TakeFirst

def change_url(value):
    if value:
        value = value.replace('/s/', '/m/')
    return value


class OtparserItem(scrapy.Item):
    name = scrapy.Field(output_processor=TakeFirst())               # постпроцессор
    photo = scrapy.Field(input_processor=MapCompose(change_url))    # препроцессор
    params = scrapy.Field()
    link = scrapy.Field()
    price = scrapy.Field()


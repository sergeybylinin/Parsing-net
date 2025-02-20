# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class InstaparserItem(scrapy.Item):
    # define the fields for your item here like:
    username = scrapy.Field()
    user_id = scrapy.Field()
    user_comment_id = scrapy.Field()
    text = scrapy.Field()
    link = scrapy.Field()
    # post_data = scrapy.Field()
    _id = scrapy.Field()

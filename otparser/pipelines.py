# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

# Для сохранения фоток важно:
#         1. В settings прописать IMAGES_STORE = 'images'
#         2. Проинсталлировать модуль pillow

import scrapy
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline


class OtparserPipeline:
    def process_item(self, item, spider):
        params_dict = dict()
        index = 0
        for el in item['params']:
            if index % 2 == 0:
                key = el[:-1]
            else:
                value = el[:-1]
                params_dict[key] = value
            index += 1
        item['params'] = params_dict
        return item


class OtPhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photo']:
            for img in item['photo']:
                try:
                    yield scrapy.Request(img)
                except TypeError as e:
                    print(e)

    def item_completed(self, results, item, info):
        if results:
            item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        directory = item['name']
        file_name = request.url
        file_name = file_name[file_name.rfind('/'): file_name.rfind('.')] + '.jpg'
        if len(file_name) > 40:
            file_name = file_name[:35] + file_name[-6:]
        return directory + file_name


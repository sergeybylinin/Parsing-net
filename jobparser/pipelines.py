# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancy
        #self.mongobase.hhru.drop()
        #self.mongobase.sjru.drop()

    def process_item(self, item, spider):

        def int_salary(st):
            return int(''.join([i for i in st if i in '0123456789']))

        def salary_format_hhru(el):
            min_salary, max_salary, currency = None, None, None

            if 'от' in el and 'до' in el:
                min_sal, arg, max_sal = el.partition('до')
                min_salary = int_salary(min_sal)
                max_salary = int_salary(max_sal)

            elif el.startswith('до'):
                max_salary = int_salary(el)

            elif el.startswith('от'):
                min_salary = int_salary(el)

            if min_salary or max_salary:
                currency = el[el.rfind(' ') + 1:].rstrip('.')

            return min_salary, max_salary, currency

        def salary_format_sjru(el):
            min_salary, max_salary, currency = None, None, None

            # if el[0] == 'По договорённости':
            #    return min_salary, max_salary, currency

            if el[0] == 'от':
                min_salary = int_salary(el[2])
                currency = ''.join(i for i in el[2] if i.isalpha())

            elif el[0] == 'до':
                max_salary = int_salary(el[2])
                currency = ''.join(i for i in el[2] if i.isalpha())

            elif el[0][0].isdigit():
                min_salary = int_salary(el[0])
                max_salary = int_salary(el[1])
                currency = ''.join(i for i in el[3] if i.isalpha())

            return min_salary, max_salary, currency


        if spider.name == 'hhru':
            salary = salary_format_hhru(item.get('salary')[0])
            item['min_salary'] = salary[0]
            item['max_salary'] = salary[1]
            item['currency'] = salary[2]
            item.pop('salary')

        if spider.name == 'sjru':
            salary = salary_format_sjru(item.get('salary'))
            item['min_salary'] = salary[0]
            item['max_salary'] = salary[1]
            item['currency'] = salary[2]
            item.pop('salary')

        collections = self.mongobase[spider.name]
        collections.insert_one(item)    # Не наполняет базу sj ???

        return item


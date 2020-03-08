# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from pydispatch import dispatcher
from scrapy import signals

from adcrawler.models import adItem

class ScrapyAppPipeline(object):
    def __init__(self, unique_id, *args, **kwargs):
        dispatcher.connect(self.spider_closed, signals.spider_closed)
        self.unique_id = unique_id

    @classmethod
    def from_crawler(cls, crawler):
        return cls( unique_id = crawler.settings.get('unique_id'))

    def process_item(self, item, spider):
        #create new django model item and add the info and save it
        django_item = adItem()

        django_item.unique_id = self.unique_id
        django_item.Title = item['Title']
        django_item.Price = item['Price']
        django_item.DateListed = item['DateListed']
        django_item.adURL = item['adURL']
        django_item.adID = item['adID']
        django_item.Description = item['Description']
        
        django_item.save()

    def spider_closed(self, spider):
        print('SPIDER FINISHED!')

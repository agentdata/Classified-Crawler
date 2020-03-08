# -*- coding: utf-8 -*-
import scrapy

# Define here the models for your scraped items
class ScrapyClassifiedItem(scrapy.Item):
    Title = scrapy.Field()
    Price = scrapy.Field()
    DateListed = scrapy.Field()
    adURL = scrapy.Field()
    adID = scrapy.Field()
    Description = scrapy.Field()
    pass
# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.spiders import CrawlSpider
from .. import items

class CrawlerSpider(CrawlSpider):
    name = 'craigslistCrawler'
    numbers = re.compile('\d+(?:\.\d+)?')

    def __init__(self, *args, **kwargs):
    # We are going to pass these args from our django view.
    # To make everything dynamic, we need to override them inside __init__ method
        self.url = kwargs.get('url')
        self.domain = kwargs.get('domain')
        self.allowed_domains = [self.domain]
        
    def start_requests(self):
        yield scrapy.Request(url = self.url, callback = self.parse_classifieds_page)

    # Get 100 search results from classifieds page to parse <div class="listing-section">
    def parse_classifieds_page(self, response):
        # Generate list of classified links on this search page which was passed here as response
        classifieds = list()
        for row in response.css("li.result-row"):
            classifieds.append(row.css("a").attrib['href'])
        
        #scrape each classified
        for classified in classifieds:
            # check if the ad has already been scraped
            yield scrapy.Request(url = classified, callback = self.parse_classified)
       
    # Parse individual classifieds and return a classified item, which includes
    def parse_classified(self, response):
        # Grab the userbody section so there is less parsing below
        adBody = response.css("section.userbody")
        
        classified = items.ScrapyClassifiedItem()
        classified['DateListed'] = adBody.css("time ::text").get()
        classified['Title'] = adBody.xpath('//*[@id="titletextonly"]/text()').get()
        
        desc = list()
        for row in adBody.xpath('//*[@id="postingbody"]/text()'):
            desc.append(row.get())
        classified['Description'] = str(''.join(desc)).strip('\n')
        # Classified['Description'] = '!static! description field area'
        
        price = response.xpath('//*[@class="price"]/text()').get()
        classified['Price'] = 0 if price == None else int(re.sub("\D", "", price))
            
        classified['adURL'] = (re.search("(?P<url>https?://[^\s]+)", str(response.request).replace('<', '').replace('>', '')).group("url"))
        classified['adID'] = str(re.sub("\D", "",adBody.xpath('//*[@class="postinginfo"]/text()').get()))

        yield classified
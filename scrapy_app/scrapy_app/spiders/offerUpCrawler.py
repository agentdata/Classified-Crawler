# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.spiders import CrawlSpider
from .. import items
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from hyperlink import URL
from attr import validate

class CrawlerSpider(CrawlSpider):
    name = 'offerUpCrawler'
    numbers = re.compile('\d+(?:\.\d+)?')

    def is_valid_url(self, url):
        validate = URLValidator()
        try:
            validate(url)
        except ValidationError:
            return False

        return True

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
        # generate list of classified links on this search page which was passed here as response
        classifieds = list()
        adBody = response.xpath('//*[@id="db-item-list"]').xpath('//*[@class="_109rpto _1anrh0x"]')
        
        # extract the URL for each classified ad in adBody section
        for row in adBody:
            if( self.is_valid_url( url=('https://www.offerup.com'+row.css("a").attrib['href'])) ):
                classifieds.append('https://www.offerup.com'+row.css("a").attrib['href'])

        # crawl the link of each classified ad
        for classified in classifieds:
            yield scrapy.Request(url = classified, callback = self.parse_classified)
       
    # Parse individual classifieds and return a classified item, which includes
    def parse_classified(self, response):
        # create classified item
        classified = items.ScrapyClassifiedItem()

        classified['Title'] = response.xpath('//*[@class="_t1q67t0 _1juw1gq"]/text()')[0].extract()
        classified['Price'] = int(re.sub("\D", "",response.xpath('//*[@class="_ckr320"]/text()').extract()[0]))
        classified['DateListed'] = '2019-7-12'
        classified['adURL'] = (re.search("(?P<url>https?://[^\s]+)", str(response.request).replace('<', '').replace('>', '')).group("url"))
        classified['adID'] = str(re.sub("\D", "",str(response.request)))

        # ## response.xpath('//*[@data-test="item-description"]/text()').extract()
        desc = list()
        for row in response.xpath('//*[@data-test="item-description"]/text()'):
            desc.append( row.get())
        classified['Description'] = str(''.join(desc)).strip('\n')

        yield classified
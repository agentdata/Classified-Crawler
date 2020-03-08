from django.test import TestCase, Client, RequestFactory
from adcrawler.models import adItem
from adcrawler.views import is_valid_url
from adcrawler.views import crawl, showExisting
from django.urls import path, reverse
from django.conf.urls import url
from django.contrib.sites import requests
import json
import time

class TestadItem(TestCase):
    # create 2 adItems
    def test_AdItem(self):
        self.adItem1 = adItem()
        self.adItem1.unique_id = "01cd4ab6-e32d-4c89-bbab-186756b1a8f8" 
        self.adItem1.Title = "Food Dehydrators For Free!"
        self.adItem1.Price = 0
        self.adItem1.DateListed = "Wed Nov 13 2019 19:21:00 GMT-0700 (Mountain Standard Time)"
        self.adItem1.adURL = "https://saltlakecity.craigslist.org/zip/d/salt-lake-city-food-dehydrators-for-free/7019403929.html"
        self.adItem1.adID = "7019403929"
        self.adItem1.Description = "These dehydrators need to be repaired, but I have been using them for a long time until a month ago."

        self.adItem2 = adItem()
        self.adItem2.unique_id = "01cd4ab6-e32d-4c89-bbab-186756b1a8f8"
        self.adItem2.Title = "Free wood chips"
        self.adItem2.Price = 0
        self.adItem2.DateListed = "Tue Nov 05 2019 16:59:00 GMT-0700 (Mountain Standard Time)"
        self.adItem2.adURL = 'https://saltlakecity.craigslist.org/zip/d/salt-lake-city-free-wood-chips/7014102857.html'
        self.adItem2.adID = "7014102857"
        self.adItem2.Description = "If you need some wood chip mulch for your garden shoot me an email. -Bryan"

        #check that the 2 models hold some data correctly and of the correct type
        self.assertNotEqual(self.adItem1, self.adItem2)
        self.assertEqual(self.adItem1.adID, "7019403929")
        self.assertEqual(self.adItem1.Description, "These dehydrators need to be repaired, but I have been using them for a long time until a month ago.")
        self.assertEquals(type(self.adItem1.Price), int)

class TestViewsAndFunctions(TestCase):
    def setUp(self):
        # this client simulates 
        self.client = Client()
        self.Factory = RequestFactory()

    def test_indexPage(self):
        #simulate hitting the home page and verify a response and correct template
        response = self.client.get(reverse('home'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'adcrawler/index.html')

    def test_isValidUrl(self):
        #check internal url validator
        self.assertTrue(is_valid_url('https://saltlakecity.craigslist.org/zip/d/salt-lake-city-free-wood-chips/7014102857.html'))
        self.assertFalse(is_valid_url('s https://saltlakecity.craigslist.org/zip/d/salt-lake-city-free-wood-chips/7014102857.html'))

    #test crawl view api Post
    def test_crawlViewPost(self):
        #test with correct post data
        goodResponse = crawl(self.Factory.post('/api/crawl/', { 'url': 'https://saltlakecity.craigslist.org/search/sss?sort=date&query=specificitem', 'crawler':'2'}))
        self.assertTrue(json.loads(goodResponse.content))

        #test with good post JSON but containing a bad URL
        badResponse = crawl(self.Factory.post('/api/crawl/', { 'url': '?https://saltlakecity.craigslist.org/search/sss?sort=date&query=specificitem'}))
        self.assertEquals(json.loads(badResponse.content), {'error': 'Bad URL'})

        #test with good post JSON but containing a bad URL
        badResponse = crawl(self.Factory.post('/api/crawl/', { 'u rl': '?https://saltlakecity.craigslist.org/search/sss?sort=date&query=specificitem'}))
        self.assertEquals(json.loads(badResponse.content), {'error': 'URL Not found'})

    #test crawl view api get
    def test_crawlViewGet(self):
        
        # test with no task id or unique id
        blankInputResponse = crawl(self.Factory.get('api/crawl/'))
        self.assertEquals(json.loads(blankInputResponse.content), {'error': 'task_id missing & unique_id missing'})

        # test with blank task id and unique id
        valuesWithBlankInputResponse = crawl(self.Factory.get('api/crawl/?task_id=&unique_id='))
        self.assertEquals(json.loads(valuesWithBlankInputResponse.content), {'error': 'task_id missing & unique_id missing'})

        # test crawl api get, with unique_id but no task_id
        validUniqueIdResponse = crawl(self.Factory.get('api/crawl/?task_id=&unique_id=79f68c6e-6e8c-4b52-adb2-7c7559aad7d9'))
        self.assertEquals(json.loads(validUniqueIdResponse.content), {'error': 'task_id missing & unique_id present'})

        # test crawl api get, with task_id but no unique_id
        validTaskIdResponse = crawl(self.Factory.get('api/crawl/?task_id=asd65423654&unique_id='))
        self.assertEquals(json.loads(validTaskIdResponse.content), {'error': 'task_id present & unique_id missing'})
        
        # test crawl api get, with task_id but no unique_id. these are bad ids and will return nothing, which means it queried scrapy successfully but found nothing.
        validBlankResponse = crawl(self.Factory.get('api/crawl/?task_id=asd654236&unique_id=asiow92'))
        self.assertEquals(json.loads(validBlankResponse.content), {'status': ''})
        
        #test good response with post data, return should have no data, because the search quer=y is nonsense
        goodPostResponse = crawl(self.Factory.post('/api/crawl/', { 'url': 'https://saltlakecity.craigslist.org/search/sss?sort=date&query=kej230932jlds', 'crawler':'2'}))
        self.assertTrue(json.loads(goodPostResponse.content))
        
        goodResponseJson = json.loads(goodPostResponse.content)
        goodTaskId = goodResponseJson.get("task_id")
        goodUniqueId = goodResponseJson.get("unique_id")

        # perform get on the task_id and unique_id in the previous statement, will not have processed yet so status will be pending
        getResults = crawl(self.Factory.get('api/crawl/?task_id='+str(goodTaskId)+'&unique_id='+str(goodUniqueId)))
        self.assertEquals(json.loads(getResults.content), {'status': 'pending'})


        ## Not sure the best way to check status running, because the time window is so small.
                
        # time.sleep(4)
        # getResults = crawl(self.Factory.get('api/crawl/?task_id='+str(goodTaskId)+'&unique_id='+str(goodUniqueId)))
        # self.assertEquals(json.loads(getResults.content), {'status': 'running'})

        # # wait 8 seconds and attempt another get,
        time.sleep(8)
        getResults = crawl(self.Factory.get('api/crawl/?task_id='+str(goodTaskId)+'&unique_id='+str(goodUniqueId)))
        self.assertEquals(json.loads(getResults.content), {'error': 'There is no data'})

    # test the showExisting view with api calls
    def test_showExisting(self):
        #regular search, but with a random searchterm that won't be in the database it will return no items found
        searchTerm = 'j3lk2mdf09m3290kjfd90'
        regularRequest = showExisting(self.Factory.get('api/showExisting/?show-searchTerm='+searchTerm))
        self.assertEquals(json.loads(regularRequest.content),  {'error': 'There were no items found with the search term "'+searchTerm+'"'})

        # submit a showexisting with a black searchterm
        regularRequest = showExisting(self.Factory.get('api/showExisting/?show-searchTerm='))
        self.assertEquals(json.loads(regularRequest.content),  {'error': 'There is no data'})
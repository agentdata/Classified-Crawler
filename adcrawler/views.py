from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from scrapyd_api import ScrapydAPI
from adcrawler.models import adItem
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from http import HTTPStatus
from urllib.parse import urlparse
from uuid import uuid4
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import requests, json

scrapyd = ScrapydAPI('http://localhost:6800')

# Create your views here.

#helper function, validates URLs
def is_valid_url(url):
    validate = URLValidator()
    try:
        validate(url)
    except ValidationError:
        return False

    return True

class SchedulingError(Exception):
    def __str__(self):
        return 'scheduling error'

# this view takes the main post/get from the crawler section of the site
# it either posts a job to 
@csrf_exempt
@require_http_methods(['POST', 'GET'])
def crawl(request):
    ## make a post to the scrapy daemon to run the job
    if request.method == 'POST':
        ## validate URL key found
        if request.POST.get('url') == None:
            return JsonResponse(
                {'error': 'URL Not found'},
                status=HTTPStatus.BAD_REQUEST
            )

        ## Validate URL second
        if not is_valid_url(request.POST.get('url')):
            return JsonResponse(
                {'error': 'Bad URL'},
                status=HTTPStatus.BAD_REQUEST
            )

        ## if post data is good, create new scrapy job with the specified spider
        domain = urlparse(request.POST.get('url')).netloc
        unique_id = str(uuid4())

        settings = {
            'unique_id': unique_id,
            'USER_AGENT': 'Chrome/78.0.3904.108',
        }

        ## define the crawler to be used
        try:
            crawler = ''
            if (request.POST.get('crawler')=='1'):
                crawler ='offerUpCrawler'
            elif (request.POST.get('crawler')=='2'):
                crawler ='craigslistCrawler'
        except Exception as e:
            return JsonResponse(
                {'error': e},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )

        try:
            task = scrapyd.schedule('default', crawler, settings = settings, url = request.POST.get('url'), domain = domain)
        except SchedulingError as e:
            return JsonResponse(
                {'error': e},
                status=HTTPStatus.INTERNAL_SERVER_ERROR
            )
        
        ## return the details returned by the scrapy daemon which can be used to check the status
        return JsonResponse({'task_id': task, 'unique_id': unique_id, 'status': 'started'})

    ## request is a GET so this will try to retrieve the data from the scrapy job with the specified unique ID and task_id
    elif request.method == 'GET':
        task_id_good = True
        unique_id_good = True
        try:
            task_id = request.GET.get('task_id')
            if (task_id == None) or (task_id == ''):
                task_id_good = False

        except ValueError as e:
            return JsonResponse(
                {'error': e},
                status = HTTPStatus.BAD_REQUEST
            )
        try:
            ## uuid regex const v4 = new RegExp(/^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$/i);
            unique_id = request.GET.get('unique_id')
            unique_id = unique_id if (unique_id == None) else unique_id.replace('/','')
            if (unique_id == None) or (unique_id == ''):
                unique_id_good = False

        except ValueError as e:
            return JsonResponse(
                {'error': e},
                status = HTTPStatus.BAD_REQUEST
            )

        ## if either task_id or unique_id are bad then return and error
        if (not task_id_good) or (not unique_id_good):
            errorMSG = ('task_id ' + ('present' if task_id_good else 'missing') + ' & unique_id ' + ('present' if unique_id_good else 'missing'))
            return JsonResponse(
                {'error': errorMSG},
                status = HTTPStatus.BAD_REQUEST
            )

        ## if task and unique ids are good request job status from scrapyd
        status = scrapyd.job_status('default', task_id)

        ## if job status is finished then get data and return it
        if status == 'finished':
            try:
                ## get list of all items in specified batch
                item = adItem.objects.filter(unique_id = unique_id)
                if not item:
                    return JsonResponse(
                        {'error': 'There is no data'},
                        status = HTTPStatus.NOT_FOUND
                    )
                ## iterate over item (list of adItems) and package as dictionary to send back to the ajax request
                dict_list = []
                for i in list(item):
                    dict_data = {
                        'Title': i.Title,
                        'DateListed': i.DateListed,
                        'Description': i.Description,
                        'Price': i.Price,
                        'adURL': i.adURL
                    }
                    dict_list.append(dict_data)
                data = {'data': dict_list}
                return JsonResponse(data)
            except Exception as e:
                return JsonResponse(
                    {'error': str(e)},
                )

        ## if job is anything other than finished, just return the current status
        else:
            return JsonResponse({'status': status})

#this view takes a get request and returns all or filtered results from the adItems database
@csrf_exempt
@require_http_methods(['GET'])
def showExisting(request):
    ## get list of all items in specified batch
    items = adItem.objects.all()

    # check if the search term is blank, if it is not blank then filter the items for 
    if (request.GET.get('show-searchTerm') != ''):
        items = items.filter(Description__icontains=(request.GET.get('show-searchTerm')))
        # if list length is 0 then return error saying that no items were found with this search term
        if(len(items) == 0):
            return JsonResponse(
            {'error': 'There were no items found with the search term "'+ request.GET.get('show-searchTerm')+'"'},
            status = HTTPStatus.NOT_FOUND
        )

    if not items:
        return JsonResponse(
            {'error': 'There is no data'},
            status = HTTPStatus.NOT_FOUND
        )

    ## iterate over item (list of adItems) and package as dictionary to send back to the client
    dict_list = []
    for i in list(items):
        dict_data = {
            'Title': i.Title,
            'DateListed': i.DateListed,
            'Description': i.Description,
            'Price': i.Price,
            'adURL': i.adURL
        }
        dict_list.append(dict_data)
    data = {'data': dict_list}
    return JsonResponse(data)
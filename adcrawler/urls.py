from django.urls import path
from django.urls import re_path, path
from django.conf import settings
from django.conf.urls import static
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    re_path(r'^$', TemplateView.as_view(template_name='adcrawler/index.html'), name='home'),
    re_path(r'^api/crawl/', views.crawl, name='crawl'),
    re_path(r'^api/showExisting/', views.showExisting, name='showExisting'),

    
]

if settings.DEBUG:
    urlpatterns += static.static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
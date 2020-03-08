from django.db import models

# Create your models here.

#note, can only grab adID(parse from listem-item-link), adURL, title, price, Address
class adItem(models.Model):
    unique_id = models.CharField(max_length=100, null=True)
    Title = models.CharField(max_length = 200)
    Price = models.IntegerField(default=None)
    DateListed = models.DateTimeField(default=None)
    adURL = models.URLField(default=None)
    adID = models.CharField(max_length = 100, default='')
    Description = models.CharField(max_length = 50000, default='')

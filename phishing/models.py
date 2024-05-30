from django.db import models

class UrlRecord(models.Model):
    url = models.URLField(max_length=2000)
    result = models.CharField(max_length=25)

from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Tweet(models.Model):
    message = models.CharField(max_length=140)
    published_date = models.DateTimeField()
    user = models.ForeignKey(User)

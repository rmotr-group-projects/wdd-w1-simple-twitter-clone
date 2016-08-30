from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Tweet(models.Model):
    user = models.CharField(max_length=140)
    #user = models.ForeignKey(User.username)#'auth.User')
    content = models.CharField(max_length=140)
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created']
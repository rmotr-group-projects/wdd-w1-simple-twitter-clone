from django.contrib.auth.models import User
from django.db import models


# Create your models here.
class Tweet(models.Model):
    content = models.CharField(max_length=140)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User)

    class Meta:
        ordering = ['-created']

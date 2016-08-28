from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login', auth_views.login, {'template_name': 'twitter/login.html'}),
    url(r'^tweet/(?P<tweet_id>[0-9]+)/delete', views.tweet_delete, name='tweet_delete'),
    url(r'^(?P<user_name>\w+)$', views.other_feed, name='other_feed'),
    url(r'^tweet_created', views.tweet_created, name='tweet_created'),
]
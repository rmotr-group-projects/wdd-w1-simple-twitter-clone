from django.conf.urls import url
from . import views

app_name = 'twitter'

urlpatterns = [
    url(r'^$', views.home_page, name='home_page'),
    url(r'^(?P<username>\w+)/$', views.user_profile, name='user_profile'),
    url(r'^delete_tweet/(?P<tweet_id>\d+)/$', views.delete_tweet, name='delete_tweet'),
]

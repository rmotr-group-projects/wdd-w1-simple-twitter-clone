from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from .models import Tweet

@login_required(login_url='/login?next=/')
def index(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/login?next=/')
    all_tweets = Tweet.objects.filter(user=request.user)
    return render(request, "twitter/authenticated_user_feed.html", {"all_tweets": all_tweets})

def login_page(request):
    return render(request, "twitter/login.html")
    
def tweet_delete(request, tweet_id):
    #/tweet/{{tweet.id}}/delete?next=/
    try:
        del_tweet = Tweet.objects.get(pk=tweet_id, user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied
    del_tweet.delete()
    return HttpResponseRedirect('/')

def other_feed(request, user_name):
    all_tweets = Tweet.objects.filter(user=user_name)#.order_by('-created')
    logged_in_user = str(request.user)
    #print(all_tweets)
    return render(request, "twitter/browsing_other_user_feed.html", {"all_tweets": all_tweets,"logged_in_user": logged_in_user, "user_name": user_name})



    
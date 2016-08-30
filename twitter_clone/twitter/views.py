from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied

from .models import Tweet

@login_required(login_url='/login?next=/')
def index(request):
    if request.method == 'POST' and request.POST['content']:
        if len(request.POST['content']) > 140:
            error = True
            content_length = len(request.POST['content'])
            all_tweets = Tweet.objects.filter(user=request.user)
            context = {
                "all_tweets": all_tweets,
                "error": error,
                "content_length": content_length
            }
            return render(request, "twitter/authenticated_user_feed.html", context)
        else:
            new_tweet = Tweet.objects.create(user=str(request.user), content=request.POST['content'])
            new_tweet.save()
            return render(request, "twitter/new_tweet_posted_successfully.html")
    
    error = None
    content_length = 0
    all_tweets = Tweet.objects.filter(user=request.user)
    context = {
        "all_tweets": all_tweets,
        "error": error,
        "content_length": content_length
    }
    return render(request, "twitter/authenticated_user_feed.html", context)

def login_page(request):
    return render(request, "twitter/login.html")

@login_required(login_url='/login?next=/')    
def tweet_delete(request, tweet_id):
    try:
        del_tweet = Tweet.objects.get(pk=tweet_id, user=request.user)
    except ObjectDoesNotExist:
        raise PermissionDenied
    del_tweet.delete()
    return HttpResponseRedirect('/')

@login_required(login_url='/login?next=/')       
def tweet_created(request):
    new_tweet = Tweet.objects.create(user=request.user, content=request.POST['content'])
    new_tweet.save()
    return HttpResponseRedirect('/')

def other_feed(request, user_name):
    all_tweets = Tweet.objects.filter(user=user_name))
    logged_in_user = str(request.user)
    return render(request, "twitter/browsing_other_user_feed.html", {"all_tweets": all_tweets,"logged_in_user": logged_in_user, "user_name": user_name})



    
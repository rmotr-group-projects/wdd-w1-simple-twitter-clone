from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def home_page(request):
    # need to check auth
    return HttpResponse("you are at twitter.home_page")


def user_profile(request, username):
    return HttpResponse("you are at twitter.user_profile for user " + username)


def post_tweet(request, tweet_id):
    return HttpResponse("you are at twitter.post_tweet with id " + tweet_id)


def delete_tweet(request, tweet_id):
    return HttpResponse("you are at twitter.delete_tweet with id " + tweet_id)


def login(request):
    return HttpResponse("you are at twitter.login")

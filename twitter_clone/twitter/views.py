from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.

def home_page(request):
    # need to check auth
    return HttpResponse("you are at twitter.home_page")


def user_profile(request):
    return HttpResponse("you are at twitter.user_profile")


def post_tweet(request):
    return HttpResponse("you are at twitter.post_tweet")


def delete_tweet(request):
    return HttpResponse("you are at twitter.delete_tweet")

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .forms import TweetForm
from .models import Tweet


# Create your views here.

@login_required
def home_page(request):
    if request.method == 'POST':
        form = TweetForm(request.POST)
        if form.is_valid():
            tweet = form.save(commit=False)
            tweet.user = request.user
            tweet.save()
            form = TweetForm()
            messages.success(request, 'Tweet created!')
    else:
        form = TweetForm()
    tweets = Tweet.objects.filter(user=request.user)
    context = {
        'form': form,
        'tweets': tweets
    }
    return render(request, 'twitter/authenticated_feed.html', context)


@require_http_methods(['GET'])
def user_profile(request, username):
    return HttpResponse("you are at twitter.user_profile for user " + username)


def delete_tweet(request, tweet_id):
    return HttpResponse("you are at twitter.delete_tweet with id " + tweet_id)

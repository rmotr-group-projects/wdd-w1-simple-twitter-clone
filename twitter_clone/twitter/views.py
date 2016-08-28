from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
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
        'tweets': tweets,
        'user': request.user.username
    }
    return render(request, 'twitter/authenticated_feed.html', context)


def user_profile(request, username):
    if request.user.is_authenticated() and username == request.user.username:
        return home_page(request)
    if request.method == 'POST':
        return HttpResponseForbidden()
    user = get_object_or_404(get_user_model(), username=username)
    tweets = Tweet.objects.filter(user=user)
    return render(request, 'twitter/base_feed.html', {'tweets': tweets, 'user': username})


@login_required
@require_http_methods(['POST'])
def delete_tweet(request, tweet_id):
    tweet = get_object_or_404(Tweet, pk=tweet_id)
    if tweet.user != request.user:
        raise PermissionDenied
    tweet.delete()
    messages.success(request, 'Tweet successfully deleted')
    return redirect(request.GET.get('next', '/'))

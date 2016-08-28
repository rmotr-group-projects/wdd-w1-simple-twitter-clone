from django.contrib.auth import get_user_model
from django_webtest import WebTest

from twitter.models import Tweet

try:
    from urllib.parse import quote
except ImportError:
    from urllib import quote

User = get_user_model()


class BaseTwitterCloneTestCase(WebTest):
    def setUp(self):
        self.jack = User.objects.create_user(
            username='jack', email='jack@twitter.com', password='coffee')
        self.ev = User.objects.create_user(
            username='evan', email='ev@twitter.com', password='coffee')

    def get_session_cookie(self, cookie_name='sessionid'):
        for cookie in self.app.cookiejar:
            if cookie.name == cookie_name:
                return cookie

    def clear_session_cookie(self):
        sid_cookie = self.get_session_cookie()

        if not sid_cookie:
            raise AttributeError("No session cookie found")

        self.app.cookiejar.clear(
            sid_cookie.domain, sid_cookie.path, sid_cookie.name)


class NotAuthenticatedTestCase(BaseTwitterCloneTestCase):
    """A not authenticated user should be redirected to the login page
    if she's trying to browse the home page, BUT she should be able
    to browse a particular profile if she has the full url.
    """

    def test_home_view_redirects_if_not_authenticated(self):
        "Should be redirected if trying to browse the home page"
        index = self.app.get('/')
        self.assertEqual(index.status_code, 302)
        self.assertTrue(index.location.endswith('/login?next=/'), index.location)

    def test_profile_view_redirects_if_not_authenticated(self):
        "Should see the profile even if not authenticated"
        index = self.app.get('/jack')
        self.assertEqual(index.status_code, 200)

    def test_login_ok_if_not_authenticated(self):
        "Should see the login page if not authenticated"
        index = self.app.get('/login')
        self.assertEqual(index.status_code, 200)


class TweetFormTestCases(BaseTwitterCloneTestCase):
    """The form to see the tweet should be visible
    only if I'm browsing my own profile as an authenticated user"""

    def test_user_browsing_profile_is_ok(self):
        index = self.app.get('/', user=self.jack)
        self.assertEqual(index.status_code, 200)

    def test_user_browsing_profile_is_sees_tweet_form(self):
        index = self.app.get('/', user=self.jack)
        self.assertEqual(index.status_code, 200)

        form = index.form
        self.assertIsNotNone(form)
        self.assertEqual(form.method, 'POST')
        self.assertEqual(form.action, '')
        content_field = form['content']
        self.assertEqual(content_field.tag, 'textarea')
        self.assertEqual(content_field.name, 'content')
        self.assertEqual(content_field.value, '')

    def test_user_browsing_other_user_doesnt_see_form(self):
        index = self.app.get('/evan', user=self.jack)
        self.assertEqual(index.status_code, 200)

        tweet_form = index.html.find('form', class_='tweet-form')
        self.assertIsNone(tweet_form)

    def test_user_browsing_own_profile_url_sees_form(self):
        index = self.app.get('/jack', user=self.jack)
        self.assertEqual(index.status_code, 200)

        form = index.form
        self.assertIsNotNone(form)
        self.assertEqual(form.method, 'POST')
        self.assertEqual(form.action, '')
        content_field = form['content']
        self.assertEqual(content_field.tag, 'textarea')
        self.assertEqual(content_field.name, 'content')
        self.assertEqual(content_field.value, '')


class CreateTweetTestCase(BaseTwitterCloneTestCase):
    def test_not_authenticated_user_cant_create_tweet(self):
        "Should return a 302 to /login if the user is not authenticated"
        index = self.app.get('/', user=self.jack)
        self.clear_session_cookie()
        form = index.form
        form['content'] = 'rmotr.com - Web Dev Django'
        response = form.submit()
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/login?next=/'))

    def test_user_cant_send_tweet_to_wrong_URL(self):
        index = self.app.get('/', user=self.jack)
        form = index.form
        form['content'] = 'rmotr.com - Web Dev Django'
        form.action = '/evan'
        response = form.submit(status=403)
        self.assertEqual(response.status_code, 403)

    def test_user_cant_post_tweet_with_more_than_140_chars(self):
        # Pre conditions
        self.assertEqual(Tweet.objects.count(), 0)

        index = self.app.get('/', user=self.jack)
        form = index.form
        form['content'] = 'a' * 141
        response = form.submit()
        div = response.form.html.find('div', class_='has-error')
        self.assertIsNotNone(div, div)
        span = div.find('span')
        self.assertIsNotNone(span)
        self.assertEqual(
            span.text,
            'Ensure this value has at most 140 characters (it has 141).')

        # Post conditions
        self.assertEqual(Tweet.objects.count(), 0)

    def test_user_can_post_tweet_successfully(self):
        # Pre conditions
        self.assertEqual(Tweet.objects.count(), 0)

        index = self.app.get('/', user=self.jack)
        form = index.form
        form['content'] = 'rmotr.com - Web Dev Django'
        response = form.submit()

        # Post conditions
        self.assertEqual(Tweet.objects.count(), 1)

        messages_div = response.html.find('div', class_='messages')
        self.assertIsNotNone(messages_div)
        success_div = messages_div.find('div', class_='alert-success')
        self.assertIsNotNone(success_div)


class BrowseProfileTestCase(BaseTwitterCloneTestCase):
    def test_user_profile_not_authenticated_shows_tweets(self):
        # Pre conditions - create a few tweets
        Tweet.objects.create(user=self.jack, content='Tweet 1')
        Tweet.objects.create(user=self.jack, content='Tweet 2')
        Tweet.objects.create(user=self.ev, content='My name is Evan')

        resp = self.app.get('/jack')
        # self.assertFalse(True, str(resp))
        # Post conditions
        feed = resp.html.find('div', class_='tweet-feed')

        tweets = feed.find_all('div', class_='tweet-container')
        self.assertEqual(len(tweets), 2)
        first, second = tweets
        self.assertEqual(
            first.find('div', class_='tweet-content').text, 'Tweet 2')
        self.assertEqual(
            second.find('div', class_='tweet-content').text, 'Tweet 1')

        # Tweets DON'T have a delete form
        self.assertIsNone(first.find('form'))
        self.assertIsNone(second.find('form'))

        # Ev's tweet is not shown
        self.assertFalse('My name is Evan' in resp.html.text)

    def test_user_profile_as_authenticated_user_shows_tweets(self):
        # Pre conditions - create a few tweets
        tweet_1 = Tweet.objects.create(user=self.jack, content='Tweet 1')
        tweet_2 = Tweet.objects.create(user=self.jack, content='Tweet 2')
        Tweet.objects.create(user=self.ev, content='My name is Evan')

        resp = self.app.get('/', user=self.jack)

        # Post conditions
        feed = resp.html.find('div', class_='tweet-feed')

        tweets = feed.find_all('div', class_='tweet-container')
        self.assertEqual(len(tweets), 2)
        first, second = tweets
        self.assertEqual(
            first.find('div', class_='tweet-content').text, 'Tweet 2')
        self.assertEqual(
            second.find('div', class_='tweet-content').text, 'Tweet 1')

        # Tweets have a delete form
        self.assertIsNotNone(first.find('form'))
        self.assertIsNotNone(second.find('form'))

        form = first.find('form')
        self.assertEqual(
            form.attrs['action'],
            "/tweet/{id}/delete?next=/".format(id=tweet_2.id))

        # Ev's tweet is not shown
        self.assertFalse('My name is Evan' in resp.html.text)


class DeleteTweetTestCase(BaseTwitterCloneTestCase):
    def test_delete_tweet_successful(self):
        # Preconditions
        tweet_1 = Tweet.objects.create(user=self.jack, content='Tweet 1')
        self.assertEqual(Tweet.objects.count(), 1)

        resp = self.app.get('/', user=self.jack)
        form = resp.forms['delete-tweet-form-{}'.format(tweet_1.id)]
        delete_resp = form.submit()

        # Post conditions
        self.assertEqual(delete_resp.status_code, 302)
        self.assertTrue(delete_resp.location.endswith('/'))
        self.assertEqual(Tweet.objects.count(), 0)

    def test_user_cant_delete_other_users_tweet(self):
        # Preconditions
        tweet_1 = Tweet.objects.create(user=self.jack, content='Tweet 1')
        tweet_2 = Tweet.objects.create(user=self.ev, content="Ev's tweet")
        self.assertEqual(Tweet.objects.count(), 2)

        resp = self.app.get('/', user=self.jack)
        form = resp.forms['delete-tweet-form-{}'.format(tweet_1.id)]
        form.action = '/tweet/{}/delete?next=/'.format(tweet_2.id)
        delete_resp = form.submit(status=403)

        # Post conditions
        self.assertEqual(delete_resp.status_code, 403)
        self.assertEqual(Tweet.objects.count(), 2)

    def test_not_authenticated_user_cant_delete_tweet(self):
        # Preconditions
        tweet_1 = Tweet.objects.create(user=self.jack, content='Tweet 1')
        self.assertEqual(Tweet.objects.count(), 1)

        resp = self.app.get('/', user=self.jack)
        form = resp.forms['delete-tweet-form-{}'.format(tweet_1.id)]
        self.clear_session_cookie()
        delete_resp = form.submit()

        # Post conditions
        self.assertEqual(delete_resp.status_code, 302)
        self.assertTrue(delete_resp.location.endswith(
            '/login?next=%s' % quote(form.action)))
        self.assertEqual(Tweet.objects.count(), 1)

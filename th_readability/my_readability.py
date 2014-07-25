# -*- coding: utf-8 -*-
# oauth and url stuff
# python 2
import sys
if sys.version_info.major == 2:
    import oauth2 as oauth
    import urlparse
# python 3
elif sys.version_info.major == 3:
    import requests_oauthlib as oauth
    from urllib.parse import urlparse

# readability API
from readability import ReaderClient

# django classes
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.log import getLogger

# django_th classes
from django_th.services.services import ServicesMgr
from django_th.models import UserService, ServicesActivated
from th_readability.models import Readability

"""
    handle process with readability
    put the following in settings.py

    TH_READABILITY = {
        'consumer_key': 'abcdefghijklmnopqrstuvwxyz',
        'consumer_secret': 'abcdefghijklmnopqrstuvwxyz',
    }

    TH_SERVICES = (
        ...
        'th_readability.my_readability.ServiceReadability',
        ...
    )

"""

logger = getLogger('django_th.trigger_happy')


class ServiceReadability(ServicesMgr):

    def __init__(self):
        base = 'https://www.readability.com'
        self.AUTH_URL = '{}/api/rest/v1/oauth/authorize/'.format(base)
        self.REQ_TOKEN = '{}/api/rest/v1/oauth/request_token/'.format(base)
        self.ACC_TOKEN = '{}/api/rest/v1/oauth/access_token/'.format(base)
        self.consumer_key = settings.TH_READABILITY['consumer_key']
        self.consumer_secret = settings.TH_READABILITY['consumer_secret']

    def process_data(self, token, trigger_id, date_triggered):
        """
            get the data from the service
        """
        data = []

        if token is not None:
            token_key, token_secret = token.split('#TH#')

            client = ReaderClient(
                self.consumer_key, self.consumer_secret,
                token_key, token_secret)

            bookmarks = client.get_bookmarks(
                added_since=date_triggered).content

            for bookmark in bookmarks.values():

                for b in bookmark:
                    if 'article' in b:
                        title = ''
                        if 'title' in b['article']:
                            title = b['article']['title']

                        link = ''
                        if 'url' in b['article']:
                            link = b['article']['url']

                        content = ''
                        if 'excerpt' in b['article']:
                            content = b['article']['excerpt']

                        data.append(
                            {'title': title,
                             'link': link,
                             'content': content})

        return data

    def save_data(self, token, trigger_id, **data):
        """
            let's save the data
        """
        if token and 'link' in data and data['link'] is not None and len(data['link']) > 0:
            # get the data of this trigger
            trigger = Readability.objects.get(trigger_id=trigger_id)
            token_key, token_secret = token.split('#TH#')
            readability_instance = ReaderClient(self.consumer_key,
                                                self.consumer_secret,
                                                token_key,
                                                token_secret)

            bookmark_id = readability_instance.add_bookmark(url=data['link'])

            if trigger.tag is not None and len(trigger.tag) > 0:
                try:
                    readability_instance.add_tags_to_bookmark(
                        bookmark_id, tags=(trigger.tag.lower()))
                    sentence = str('readability {} created item id {}').format(
                        data['link'], bookmark_id)
                    logger.debug(sentence)
                except Exception as e:
                    logger.critical(e)
        else:
            sentence = "no token or link provided for trigger ID {} "
            logger.critical(sentence.format(trigger_id))

    def auth(self, request):
        """
            let's auth the user to the Service
        """

        callbackUrl = 'http://%s%s' % (
            request.get_host(), reverse('readability_callback'))
        request_token = self.get_request_token(request, callbackUrl)

        # Save the request token information for later
        request.session['oauth_token'] = request_token['oauth_token']
        request.session['oauth_token_secret'] = request_token[
            'oauth_token_secret']

        # URL to redirect user to, to authorize your app
        auth_url = self.get_auth_url(request, request_token)

        return auth_url

    def callback(self, request):
        """
            Called from the Service when the user accept to activate it
        """

        try:
            # finally we save the user auth token
            # As we already stored the object ServicesActivated
            # from the UserServiceCreateView now we update the same
            # object to the database so :
            # 1) we get the previous objet
            us = UserService.objects.get(
                user=request.user,
                name=ServicesActivated.objects.get(name='ServiceReadability'))
            # 2) Readability API require to use 4 parms consumer_key/secret +
            # token_key/secret instead of usually get just the token
            # from an access_token request. So we need to add a string
            # seperator for later use to slpit on this one
            access_token = self.get_access_token(
                request.session['oauth_token'],
                request.session['oauth_token_secret'],
                request.GET.get('oauth_verifier', '')
            )
            us.token = access_token['oauth_token'] + \
                '#TH#' + access_token['oauth_token_secret']

            # 3) and save everything
            us.save()
        except KeyError:
            return '/'

        return 'readability/callback.html'

    # Oauth Stuff
    def get_auth_url(self, request, request_token):
        return '%s?oauth_token=%s' % (
            self.AUTH_URL,
            urllib.quote(request_token['oauth_token']))

    def get_request_token(self, request, callback_url):
        client = self._get_oauth_client()
        request_url = '%s?oauth_callback=%s' % (
            self.REQ_TOKEN, urllib.quote(callback_url))

        resp, content = client.request(request_url, 'GET')
        request_token = dict(urlparse.parse_qsl(content))
        return request_token

    def get_access_token(
        self, oauth_token, oauth_token_secret, oauth_verifier
    ):
        token = oauth.Token(oauth_token, oauth_token_secret)
        token.set_verifier(oauth_verifier)
        client = self._get_oauth_client(token)

        resp, content = client.request(self.ACC_TOKEN, 'POST')
        access_token = dict(urlparse.parse_qsl(content))
        return access_token

    def _get_oauth_client(self, token=None):
        consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        if token:
            client = oauth.Client(consumer, token)
        else:
            client = oauth.Client(consumer)
        return client

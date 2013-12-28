# -*- coding: utf-8 -*-

# django_th classes
from django_th.services.services import ServicesMgr
from django_th.models import UserService, ServicesActivated
# django classes
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.log import getLogger

# oauth and url stuff
import oauth2 as oauth
import urlparse
import urllib
# import arrow

# add the python API here if needed
from readability import ReaderClient

"""
    handle process with readability
    put the following in settings.py

    TH_READABILITY = {
        'consummer_key': 'abcdefghijklmnopqrstuvwxyz',
        'consummer_secret': 'abcdefghijklmnopqrstuvwxyz',
    }

"""

logger = getLogger('django_th.trigger_happy')


class ServiceReadability(ServicesMgr):

    def __init__(self):
        self.AUTH_URL = 'https://www.readability.com/api/rest/v1/oauth/authorize/'
        self.REQ_TOKEN = 'https://www.readability.com/api/rest/v1/oauth/request_token/'
        self.ACC_TOKEN = 'https://www.readability.com/api/rest/v1/oauth/access_token/'
        self.consummer_key = settings.TH_READABILITY['consummer_key']
        self.consummer_secret = settings.TH_READABILITY['consummer_secret']

    def process_data(self, token, trigger_id, date_triggered):
        """
            get the data from the service
        """
        data = []

        if token is not None:
            token_key, token_secret = token.split('#TH#')

            client = ReaderClient(self.consummer_key, self.consummer_secret,
                                  token_key, token_secret)

            date_triggered = '20130101 00:00:00'  # for test purpose
            bookmarks = client.get_bookmarks(added_since=date_triggered)

            for bookmark in bookmarks:

                data.append(
                    {'title': bookmark.article.title,
                     'link': bookmark.article.link,
                     'content': bookmark.article.excerpt})

        return data

    def save_data(self, token, trigger_id, **data):
        """
            let's save the data
        """
        from th_readability.models import readability

        if token and 'link' in data and data['link'] is not None and len(data['link']) > 0:
            # get the data of this trigger
            trigger = readability.objects.get(trigger_id=trigger_id)
            token_key, token_secret = token.split('#TH#')
            readability_instance = ReaderClient(self.consummer_key,
                                                self.consummer_secret,
                                                token_key,
                                                token_secret)

            title = ''
            title = (data['title'] if 'title' in data else '')
            # add data to the external service
            item_id = readability_instance.add(
                url=data['link'], title=title, tags=(trigger.tag.lower()))

            sentance = str('readability {} created item id {}').format(
                data['link'], item_id)
            logger.debug(sentance)
        else:
            logger.critical("no token provided for trigger ID %s ", trigger_id)

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
            # 2) Readability API require to use 4 parms consummer_key/secret + token_key/secret
            # instead of usually get just the token from an access_token
            # request. So we need to add a string seperator for later use to
            # slpit on this one
            access_token = request.session[
                'oauth_token'] + '#TH#' + request.session['oauth_token_secret']

            us.token = access_token
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
        consummer = oauth.Consumer(self.consummer_key, self.consummer_secret)

        client = oauth.Client(consummer)

        request_url = '%s?oauth_callback=%s' % (
            self.REQ_TOKEN, urllib.quote(callback_url))

        resp, content = client.request(request_url, 'GET')
        request_token = dict(urlparse.parse_qsl(content))
        return request_token

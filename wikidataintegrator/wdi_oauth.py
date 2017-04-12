from mwoauth import ConsumerToken, Handshaker
from requests_oauthlib import OAuth1
import requests
import webbrowser
import time

__author__ = 'timputman'

class WDOauth(object):
    """
    a wrapper class for mwoauth to handle consumer key and secret redirect and supply an access token
    """

    def __init__(self, consumer_key, consumer_secret, bot=False):
        """

        :param consumer_key:
        :param consumer_token:
        :return: object with authentication object, edit token  and user information from MediaWiki
        """
        self.bot = bot
        self.wd_url = 'https://www.wikidata.org/w/api.php'
        self.mw_url = "https://www.mediawiki.org/w/index.php"
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret

        # Consruct a "consumer" from the key/secret provided by MediaWiki
        self.consumer_token = ConsumerToken(self.consumer_key, self.consumer_secret)

        # Construct handshaker with wiki URI and consumer
        self.handshaker = Handshaker(self.mw_url, self.consumer_token)

        # Step 1: Initialize -- ask MediaWiki for a temp key/secret for user
        # redirect -> authorization -> callback url
        self.redirect, self.request_token = self.handshaker.initiate()
        self.response_qs = ''
        webbrowser.open(self.redirect)

    def generate_authentication_object(self, query_string=None):
        if self.bot:
            self.response_qs = input("Response query string: ")
        else:
            self.response_qs = query_string

        # input the url from redirect after authorization
        response_qs = self.response_qs.split("?")[-1]

        # Step 3: Complete -- obtain authorized key/secret for "resource owner"
        access_token = self.handshaker.complete(self.request_token, response_qs)
        identity = self.handshaker.identify(access_token)

        # input the access token to return a csrf (edit) token
        auth1 = OAuth1(self.consumer_token.key,
                       client_secret=self.consumer_token.secret,
                       resource_owner_key=access_token.key,
                       resource_owner_secret=access_token.secret)

        response_token = requests.get(self.wd_url,
                                      params={
                                          'action': "query",
                                          'meta': "tokens",
                                          'format': "json"
                                      },
                                      auth=auth1
                                      )
        authentication_object = {
            'base_url': self.wd_url,
            'oauth': {'authorization': auth1,
                      'identity': identity,
                      },
            'server': 'www.wikidata.org',
            'token_renew_period': 1800,
            'edit_token': response_token.json()['query']['tokens']['csrftoken'],
            'instantiation_time': time.time(),
            's': False
        }

        return authentication_object

        # Walkthrough at https://www.mediawiki.org/wiki/OAuth/For_Developers

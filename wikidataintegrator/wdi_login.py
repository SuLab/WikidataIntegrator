import time
import requests
import webbrowser

from mwoauth import ConsumerToken, Handshaker
from requests_oauthlib import OAuth1


from wikidataintegrator.backoff.wdi_backoff import wdi_backoff, get_config

__author__ = 'Sebastian Burgstaller-Muehlbacher, Tim Putman, Andra Waagmeester'
__license__ = 'AGPLv3'

"""
Login class for Wikidata. Takes username and password and stores the session cookies and edit tokens.
"""


class WDLogin(object):
    """
    A class which handles the login to Wikidata and the generation of edit-tokens
    """

    @wdi_backoff()
    def __init__(self, user=None, pwd=None, server='www.wikidata.org', token_renew_period=1800, use_clientlogin=False,
                 consumer_key=None, consumer_secret=None, callback_url='oob'):
        """
        This class handles several types of login procedures. Either use user and pwd authentication or OAuth. 
        Wikidata clientlogin can also be used. If using one method, do NOT pass parameters for another method. 
        :param user: the username which should be used for the login
        :param pwd: the password which should be used for the login
        :param server: the wikimedia server the login should be made to
        :param token_renew_period: Seconds after which a new token should be requested from the Wikidata server
        :type token_renew_period: int
        :param use_clientlogin: use authmanager based login method instead of standard login.
            For 3rd party data consumer, e.g. web clients
        :type bool
        :param consumer_key: The consumer key for OAuth
        :type consumer_key: str
        :param consumer_secret: The consumer secret for OAuth
        :type consumer_secret: str
        :param callback_url: URL which should be used as the callback URL
        :type callback_url: str
        :return: None
        """
        if server is not None:
            self.server = server
        self.base_url = 'https://{}/w/api.php'.format(self.server)
        self.s = requests.Session()

        self.edit_token = ''
        self.instantiation_time = time.time()
        self.token_renew_period = token_renew_period

        self.mw_url = "https://www.mediawiki.org/w/index.php"
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.response_qs = None
        self.callback_url = callback_url

        if self.consumer_key and self.consumer_secret:
            # Oauth procedure, based on https://www.mediawiki.org/wiki/OAuth/For_Developers

            # Consruct a "consumer" from the key/secret provided by MediaWiki
            self.consumer_token = ConsumerToken(self.consumer_key, self.consumer_secret)

            # Construct handshaker with wiki URI and consumer
            self.handshaker = Handshaker(self.mw_url, self.consumer_token, callback=self.callback_url)

            # Step 1: Initialize -- ask MediaWiki for a temp key/secret for user
            # redirect -> authorization -> callback url
            self.redirect, self.request_token = self.handshaker.initiate(callback=self.callback_url)

        elif use_clientlogin:
            params = {
                'action': 'query',
                'format': 'json',
                'meta': 'authmanagerinfo',
                'amisecuritysensitiveoperation': '',
                'amirequestsfor': 'login'
            }

            self.s.get(self.base_url, params=params)

            params2 = {
                'action': 'query',
                'format': 'json',
                'meta': 'tokens',
                'type': 'login'
            }
            login_token = self.s.get(self.base_url, params=params2).json()['query']['tokens']['logintoken']

            data = {
                'action': 'clientlogin',
                'format': 'json',
                'username': user,
                'password': pwd,
                'logintoken': login_token,
                'loginreturnurl': 'http://example.org/'
            }

            login_result = self.s.post(self.base_url, data=data).json()
            print(login_result)

            if login_result['clientlogin']['status'] == 'FAIL':
                raise ValueError('Login FAILED')

            self.generate_edit_credentials()
        else:
            params = {
                'action': 'login',
                'lgname': user,
                'lgpassword': pwd,
                'format': 'json'
            }

            # get login token
            login_token = self.s.post(self.base_url, data=params).json()['login']['token']

            # do the login using the login token
            params.update({'lgtoken': login_token})
            r = self.s.post(self.base_url, data=params).json()

            if r['login']['result'] != 'Success':
                print('login failed:', r['login']['reason'])
                raise ValueError('login FAILED!!')
            else:
                print('Successfully logged in as', r['login']['lgusername'])

            self.generate_edit_credentials()

    def generate_edit_credentials(self):
        """
        request an edit token and update the cookie_jar in order to add the session cookie
        :return: Returns a json with all relevant cookies, aka cookie jar
        """
        params = {
            'action': 'query',
            'meta': 'tokens',
            'format': 'json'
        }
        response = self.s.get(self.base_url, params=params)
        self.edit_token = response.json()['query']['tokens']['csrftoken']

        return self.s.cookies

    def get_edit_cookie(self):
        """
        Can be called in order to retrieve the cookies from an instance of WDLogin
        :return: Returns a json with all relevant cookies, aka cookie jar
        """
        if (time.time() - self.instantiation_time) > self.token_renew_period:
            self.generate_edit_credentials()
            self.instantiation_time = time.time()

        return self.s.cookies

    def get_edit_token(self):
        """
        Can be called in order to retrieve the edit token from an instance of WDLogin
        :return: returns the edit token
        """
        if not self.edit_token or (time.time() - self.instantiation_time) > self.token_renew_period:
            self.generate_edit_credentials()
            self.instantiation_time = time.time()

        return self.edit_token

    def get_session(self):
        """
        returns the requests session object used for the login.
        :return: Object of type requests.Session()
        """
        return self.s

    def continue_oauth(self, oauth_callback_data=None):
        """
        Continuation of OAuth procedure. Method must be explicitly called in order to complete OAuth. This allows 
        external entities, e.g. websites, to provide tokens through callback URLs directly.
        :param oauth_callback_data: The callback URL received to a Web app
        :type oauth_callback_data: str
        :return: 
        """
        self.response_qs = oauth_callback_data

        if not self.response_qs:
            webbrowser.open(self.redirect)
            self.response_qs = input("Callback URL: ")

        # input the url from redirect after authorization
        response_qs = self.response_qs.split("?")[-1]

        # Step 3: Complete -- obtain authorized key/secret for "resource owner"
        access_token = self.handshaker.complete(self.request_token, response_qs)

        # input the access token to return a csrf (edit) token
        auth1 = OAuth1(self.consumer_token.key,
                       client_secret=self.consumer_token.secret,
                       resource_owner_key=access_token.key,
                       resource_owner_secret=access_token.secret)

        self.s.auth = auth1
        self.generate_edit_credentials()

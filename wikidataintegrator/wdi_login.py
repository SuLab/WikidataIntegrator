import time

import requests

from wikidataintegrator.backoff.wdi_backoff import wdi_backoff, get_config

__author__ = 'Andra Waagmeester and Sebastian Burgstaller'
__license__ = 'AGPLv3'

"""
Login class for Wikidata. Takes username and password and stores the session cookies and edit tokens.
"""


class WDLogin(object):
    """
    A class which handles the login to Wikidata and the generation of edit-tokens
    """

    @wdi_backoff()
    def __init__(self, user, pwd, server='www.wikidata.org', token_renew_period=1800, use_clientlogin=False):
        """
        constructor
        :param user: the username which should be used for the login
        :param pwd: the password which should be used for the login
        :param server: the wikimedia server the login should be made to
        :param token_renew_period: Seconds after which a new token should be requested from the Wikidata server
        :type token_renew_period: int
        :param use_clientlogin: use authmanager based login method instead of standard login.
            For 3rd party data consumer, e.g. web clients
        :type bool
        :return: None
        """
        if server is not None:
            self.server = server
        self.base_url = 'https://{}/w/api.php'.format(self.server)
        self.s = requests.Session()

        self.edit_token = ''
        self.instantiation_time = time.time()
        self.token_renew_period = token_renew_period

        if use_clientlogin:
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

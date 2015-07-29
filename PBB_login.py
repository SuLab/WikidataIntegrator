__author__ = 'Andra Waagmeester and Sebastian Burgstaller'
__license__ = 'GPLv3'

"""
login routine for Wikidata
"""
import requests
import time


class WDLogin(object):
    """
    A class which handles the login to Wikidata and the generation of edit-tokens
    """
    user = ''
    pwd = ''
    server = 'www.wikidata.org'
    cookie_jar = {}
    edit_token = ''
    baseurl = ''
    instantiation_time = time.time()
    token_renew_period = 1800

    def __init__(self, user, pwd, server='www.wikidata.org', token_renew_period=1800):
        """
        constructor
        :param user: the username which should be used for the login
        :param pwd: the password which should be used for the login
        :param server: the wikimedia server the login should be made to
        :param token_renew_period: Seconds after which a new token should be requested from the Wikidata server
        :type token_renew_period: int
        :return: None
        """
        self.user = user
        self.pwd = pwd
        if server is not None:
            self.server = server

        self.instantiation_time = time.time()
        self.token_renew_period = token_renew_period

        self.baseurl = 'https://' + self.server + '/w/api.php'

        # Get login token and cookie
        params = {
            'action': 'login',
            'lgname': self.user,
            'lgpassword': self.pwd,
            'format': 'json'
        }

        response1 = requests.post(self.baseurl, params=params)
        cookies = response1.cookies
        login_token = response1.json()['login']['token']
        self.token = login_token
        
        # do the login using the login token
        params.update({'lgtoken': login_token})
        response2 = requests.post(self.baseurl, params=params, cookies=cookies)
        self.cookie_jar = response2.cookies.copy()

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
        response = requests.get(self.baseurl, params=params, cookies=self.cookie_jar)
        self.edit_token = response.json()['query']['tokens']['csrftoken']

        self.cookie_jar.update(response.cookies)

        return self.cookie_jar

    def get_edit_cookie(self):
        """
        Can be called in order to retrieve the cookies from an instance of WDLogin
        :return: Returns a json with all relevant cookies, aka cookie jar
        """
        if self.cookie_jar is {} or (time.time() - self.instantiation_time) > self.token_renew_period:
            self.generate_edit_credentials()
            self.instantiation_time = time.time()

        return self.cookie_jar

    def get_edit_token(self):
        """
        Can be called in order to retrieve the edit token from an instance of WDLogin
        :return: returns the edit token
        """
        if self.edit_token is '' or (time.time() - self.instantiation_time) > self.token_renew_period:
            self.generate_edit_credentials()
            self.instantiation_time = time.time()

        return self.edit_token

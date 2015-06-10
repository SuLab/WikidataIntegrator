__author__ = 'Andra Waagmeester and Sebastian Burgstaller'
__license__ = 'GPL'


"""
login routine for Wikidata
"""
import urllib2
import pprint
import requests
try: import simplejson as json
except ImportError: import json # http://stackoverflow.com/a/712799/155046

def login(user, password):
    # Login to wikidata
    baseurl = 'http://www.wikidata.org/w/'
    login_params = '?action=login&lgname=%s&lgpassword=%s&format=json'%(user, password)
    wdapi = 'http://www.wikidata.org/w/api.php?action=login'
    r1= requests.post(baseurl+'api.php'+login_params)
    return r1.json()
    
def prettyPrint(variable):
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(variable)
    
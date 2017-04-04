"""
Set up backoff module for wikidataintegrator

"""

import sys
from functools import partial

import requests

from wikidataintegrator.backoff import backoff
from wikidataintegrator.wdi_config import config


import simplejson as json

JSONDecodeError = json.JSONDecodeError


def get_config(name):
    return partial(config.get, name)


def backoff_hdlr(details):
    exc_type, exc_value, _ = sys.exc_info()
    if exc_type == JSONDecodeError:
        print(exc_value.doc)
    print("Backing off {wait:0.1f} seconds afters {tries} tries "
          "calling function with args {args} and kwargs "
          "{kwargs}".format(**details))


def check_json_decode_error(e):
    """
    Check if the error message is "Expecting value: line 1 column 1 (char 0)"
    if not, its a real error and we shouldn't retry
    :param e:
    :return:
    """
    return type(e) == JSONDecodeError and str(e) != "Expecting value: line 1 column 1 (char 0)"


exceptions = (requests.exceptions.Timeout, requests.exceptions.ConnectionError,
              requests.HTTPError, JSONDecodeError)
wdi_backoff = partial(backoff.on_exception, backoff.expo, exceptions, max_value=get_config("BACKOFF_MAX_VALUE"),
                      giveup=check_json_decode_error, on_backoff=backoff_hdlr, jitter=None,
                      max_tries=get_config("BACKOFF_MAX_TRIES"))

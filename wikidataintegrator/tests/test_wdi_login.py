from __future__ import print_function
import sys

from wikidataintegrator import wdi_login
import os

# look for environment variables. if none set, don't do anything
WDUSER = os.getenv("WDUSER")
WDPASS = os.getenv("WDPASS")


def test_login():
    if WDUSER and WDPASS:
        login = wdi_login.WDLogin(WDUSER, WDPASS)
    else:
        print("no WDUSER or WDPASS found in environment variables", file=sys.stderr)

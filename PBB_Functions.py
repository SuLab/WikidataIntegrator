#!usr/bin/env python
# -*- coding: utf-8 -*-

'''
Authors: 
  Sebastian Burgstaller (sebastian.burgstaller' at 'gmail.com
  Andra Waagmeester (andra' at ' micelio.be)

This file is part of ProteinBoxBot.

ProteinBoxBot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ProteinBoxBot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ProteinBoxBot.  If not, see <http://www.gnu.org/licenses/>.
'''

__author__ = 'Sebastian Burgstaller, Andra Waagmeester'
__license__ = 'GPL'

import PBB_Debug
import PBB_login
import PBB_settings
import requests
import wd_property_store
import urllib2
try: import simplejson as json
except ImportError: import json # http://stackoverflow.com/a/712799/155046

def getItemsByProperty(wdproperty):
    """
    Gets all WikiData item IDs that contains statements containing property wdproperty
    """
    req = urllib2.Request("http://wdq.wmflabs.org/api?q=claim%5B"+wdproperty+"%5D&props="+wdproperty, None, {'user-agent':'proteinBoxBot'})
    opener = urllib2.build_opener()
    f = opener.open(req)
    return json.load(f)
    
def write(wd_json_representation, wd_item_id, server):
    """
    function to initiate writing the item data in the instance to Wikidata
    :param login: a instance of the class PBB_login which provides edit-cookies and edit-tokens
    :return: None
    """
    login = PBB_login.WDLogin(PBB_settings.getWikiDataUser(), PBB_settings.getWikiDataPassword())
    cookies = login.get_edit_cookie()
    edit_token = login.get_edit_token()

    headers = {'content-type': 'application/x-www-form-urlencoded'}
    payload = {
        'action': 'wbeditentity',
        'data': '{}'.format(str(wd_json_representation)),
        'format': 'json',
        'token': edit_token
    }

    #if self.create_new_item:
    #    payload.update({'new': 'item'})
    # else:
        
    payload.update({'id': wd_item_id})

    base_url = 'https://' + server + '/w/api.php'

    try:
        reply = requests.post(base_url, headers=headers, data=payload, cookies=cookies)
        print reply
        json_data = json.loads(reply.text)
        PBB_Debug.prettyPrint(json_data)

    except requests.HTTPError as e:
        print(e)
        PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())

    
    
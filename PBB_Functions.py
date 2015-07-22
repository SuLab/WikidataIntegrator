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

try: import simplejson as json
except ImportError: import json # http://stackoverflow.com/a/712799/155046

def getItemsByProperty(wdproperty):
    """
    Gets all WikiData item IDs that contains statements containing property wdproperty
    """
    req = requests.get("http://wdq.wmflabs.org/api?q=claim%5B"+wdproperty+"%5D&props="+wdproperty, headers={'user-agent':'proteinBoxBot'})

    return req.json()
    


    
    
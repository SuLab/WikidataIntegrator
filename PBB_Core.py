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

import pywikibot
from pywikibot.data import api
import json
import urllib2

class WDItemEngine(object):

    def __init__(self, wd_item_id='', item_names=[]):
        self.wd_item_id = wd_item_id
        self.item_names = item_names
        self.autoadd_references = False

    @classmethod
    def get_item_data(cls, item_name=None, item_id=None):
        """
        Instantiate a class by either providing a item name or a Wikidata item ID
        :param item_name: A name which should allow to find an item in Wikidata
        :param item_id: Wikidata item ID which allows loading of a Wikidata item
        :return: None
        """
        if item_name is None and item_id is None:
            raise IDMissingError('No item name or WD identifyer was given')

        try:
            title_string = ''
            if item_id is not None:
                title_string = '&ids={}'.format(item_id)
            elif item_name is not None:
                title_string = '&titles={}'.format(item_name.replace(' ', '%20'))

            query = 'https://www.wikidata.org/w/api.php?action=wbgetentities{}{}{}{}{}{}'.format(
                '&sites=enwiki',
                '&languages=en',
                title_string,
                '&props=labels|aliases|claims',
                '&normalize=',
                '&format=json'
            )

            return(json.load(urllib2.urlopen(query)))

        except urllib2.HTTPError as e:
            print(e)

    @classmethod
    def add_property(cls, property):
        """
        :param property: takes a property the WDItem should have
        :return: None
        """
        pass

    @classmethod
    def add_reference(cls, property, reference_type, reference_item):
        """
        Call this method to add a reference to a property
        :param property: the Wikidata property number a reference should be added to
        :param reference_type: The reference property number (e.g. stated in (P248), imported from (P143))
        :param reference_item: the item a reference should point to
        :return: None
        """
        pass

    @classmethod
    def autoadd_references(cls, refernce_type, reference_item):
        """
        adds a reference to all properties of a WD item
        :param refernce_type:
        :param reference_item:
        :return:
        """

    def check_integrity(self, property_list):
        """
        Invokes the check of integrity of an item, i.e. if labels are consistent and properties fit to the domain
        :param a list with WD property numbers (strings) which are used to check for integrity
        :return:
        """
        pass

    def set_label(self, label):
        """
        set the label for a WD item
        :param label: a label string as the wikidata item.
        :return: None
        """

        setattr(self, 'label', label)

    def set_aliases(self, aliases):
        """
        set the aliases for a WD item
        :param aliases: a list of strings representing the aliases of a WD item
        :return: None
        """

    @classmethod
    def write(cls):
        """
        function to initiate writing the item data in the instance to Wikidata
        :return:
        """
        pass





class IDMissingError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
>>>>>>> External Changes

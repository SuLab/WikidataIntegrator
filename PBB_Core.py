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

import time
import datetime
import urllib
import urllib3
import certifi
import itertools
import requests

import PBB_Debug
import PBB_Functions
import PBB_settings
import mysql.connector
import socket
import getpass
import copy

import wd_property_store
try:
    import simplejson as json
except ImportError as e:
    import json


class BotMainLog():
    def __init__(self):
        self.bot = ''
        self.start_date = ''
        self.finish_date = ''
        self.bot_ip = socket.gethostbyname(socket.gethostname())
        self.bot_user = getpass.getuser()
            
    def connectDb(self):
        return mysql.connector.connect(user=PBB_settings.getMySQLUser(), password=PBB_settings.getMySQLPW(),
                                      host=PBB_settings.getMySQLHost(),
                                      database='ProteinBoxBot')
    
    def addTuple(self):
        cnx = self.connectDb()
        cursor = cnx.cursor()
        sql_tuple = ("INSERT INTO PBB_History "
                    "(bot, start_date, finish_date, bot_ip, bot_user) "
                    "VALUES (%s, %s, %s, %s, %s)")
        data_tuple = (self.bot, self.start_date, self.finish_date, self.bot_ip, self.bot_user)
        print self.bot
        print self.start_date
        print self.finish_date
        print cursor.execute(sql_tuple, data_tuple)
        cnx.commit()
        
        # print all the first cell of all the rows
        # Use all the SQL you like
        cursor.execute("SELECT * FROM PBB_History")
        for row in cursor.fetchall() :
            print row[0]


class WDItemList(object):
    def __init__(self, wdquery = "", wdprop=""):
        self.wdquery = wdquery
        self.wditems = self.getItemsByProperty(wdquery, wdprop)

    def getItemsByProperty(self, wdquery, wdproperty):
        """
        Gets all WikiData item IDs that contains statements containing property wdproperty
        :param wdquery: A string representation of a WD query
        :return: A Python json representation object with the search results is returned
        """
        http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
        req = http.request("GET", "http://wdq.wmflabs.org/api?"+urllib.urlencode({"q":wdquery, "props":wdproperty}))
        return json.loads(req.data)


class WDItemEngine(object):

    wd_item_id = ''
    item_names = ''
    domain = ''
    autoadd_references = False
    normalize = True
    create_new_item = False
    data = {}
    append_value = []
    server = 'www.wikidata.org'

    # a list with all properties an item should have and/or modify
    property_list = {}
    wd_json_representation = ''

    def __init__(self, wd_item_id='', item_name='', normalize=True, domain='', data={}, token='', server='', append_value=[]):
        """
        constructor
        :param wd_item_id: Wikidata item id
        :param item_name: Label of the wikidata item
        :param normalize: boolean if wbgetentity should use the parameter normalize
        :param domain: string which tells the data domain the class should operate in
        :param data: a dictionary with WD property strings as keys and the data which should be written to
        a WD item as the property values
        :param append_value: a list of properties where potential existing values should not be overwritten by the data
        passed in the :parameter data.
        """
        self.wd_item_id = wd_item_id
        self.item_names = item_name
        self.domain = domain
        self.autoadd_references = False
        self.normalize = normalize
        self.data = data
        self.token = token
        self.server = server
        self.append_value = append_value

        self.get_item_data(item_name, wd_item_id)
        self.property_list = self.get_property_list()

        self.__construct_claim_json()

    def get_item_data(self, item_name='', item_id=''):
        """
        Instantiate a class by either providing a item name or a Wikidata item ID
        :param item_name: A name which should allow to find an item in Wikidata
        :param item_id: Wikidata item ID which allows loading of a Wikidata item
        :return: None
        """
        if item_name is '' and item_id is '':
            raise IDMissingError('No item name or WD identifier was given')
        elif item_id is not '':
            self.wd_json_representation = self.get_wd_entity(item_id)
        else:
            try:
                qids_by_string_search = self.get_wd_search_results(item_name)
                qids_by_props = self.__select_wd_item(item_list=qids_by_string_search, item_labels=[])

            except WDSearchError as e:
                PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
                print(e)
                qids_by_props = self.__select_wd_item([])

            if qids_by_props is not '':
                self.wd_item_id = 'Q{}'.format(qids_by_props)
                self.wd_json_representation = self.get_wd_entity(self.wd_item_id)

    def get_wd_entity(self, item=''):
        """
        retrieve a WD item in json representation from Wikidata
        :param item: string which represents the wikidata QID
        :return: python complex dictionary represenation of a json
        """
        try:
            query = 'https://{}/w/api.php?action=wbgetentities{}{}{}{}'.format(
                self.server,
                '&sites=enwiki',
                '&languages=en',
                '&ids={}'.format(item),
                '&format=json'
            )
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            request = http.request("GET", query)

            wd_reply = json.loads(request.data)['entities'][self.wd_item_id]
            wd_reply = {x: wd_reply[x] for x in ('labels', 'descriptions', 'claims', 'aliases', 'sitelinks') if x in wd_reply}
            return(wd_reply)

        except urllib3.exceptions.HTTPError as e:
            PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
            print(e)

    def get_wd_search_results(self, search_string=''):
        """
        Performs a search in WD for a certain WD search string
        :param search_string: a string which should be searched for in WD
        :return: returns a list of QIDs found in the search and a list of labels complementary to the QIDs
        """
        try:
            query = 'https://{}/w/api.php?action=wbsearchentities{}{}{}'.format(
                self.server,
                '&language=en',
                '&search=' + urllib.quote(search_string),
                '&format=json'
            )
            print query
            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
            request = http.request("GET", query)
            search_results = json.loads(request.data)

            if search_results['success'] != 1:
                raise WDSearchError('WD search failed')
            elif len(search_results['search']) == 0:
                return([])
            else:
                id_list = []
                id_labels = []
                for i in search_results['search']:
                    id_list.append(i['id'])
                    id_labels.append(i['label'])

                return(id_list)

        except urllib3.exceptions.HTTPError as e:
            print(e)
            PBB_Debug.getSentryClient().captureException(e)

    def get_property_list(self):
        """
        extract the properties which belong to the domain of the WD item
        :return: a dict with WD property strings as keys and empty strings as values
        """
        property_list = []
        for x in wd_property_store.wd_properties:
            if self.domain in wd_property_store.wd_properties[x]['domain']:
                property_list.append(x)

        return(property_list)

    def __select_wd_item(self, item_list, item_labels):
        """
        The most likely WD item QID should be returned, after querying WDQ for all core_id properties
        :param item_list: a list of QIDs returned by a string search in WD
        :param item_labels: a complementary list of WD item labels to the QIDs from param item_list
        :return:
        """
        qid_list = []
        for wd_property in self.data:
            if wd_property in wd_property_store.wd_properties:
                try:
                    # check if the property is a core_id and should be unique for every WD item
                    if wd_property_store.wd_properties[wd_property]['core_id'] == 'True':
                        for data_point in self.data[wd_property]:
                            query = 'http://wdq.wmflabs.org/api?q=string[{}:{}]'.format(wd_property.replace('P', ''), urllib.quote(str(data_point)))
                            http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())
                            request = http.request("GET", query)
                            tmp_qids = json.loads(request.data)['items']
                            qid_list.append(tmp_qids)

                            if len(tmp_qids) > 1:
                                raise ManualInterventionReqException('More than one WD item has the same property value', wd_property, tmp_qids)

                except urllib3.exceptions.HTTPError as e:
                    PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
                    print(e)

        qid_list = [i for i in itertools.chain.from_iterable(qid_list)]

        if len(qid_list) == 0:
            self.create_new_item = True
            return('')

        print(qid_list)

        unique_qids = set(qid_list)
        if len(unique_qids) > 1:
            # FIX: exception should be given a list at param 2 which properties are causing the conflicts
            raise ManualInterventionReqException('More than one WD item has the same property value', 'implementation req', unique_qids)
        elif len(unique_qids) == 1:
            return(list(unique_qids)[0])

    def __construct_claim_json(self):
        """
        Writes the properties from self.data to a new or existing json in self.wd_json_representation
        :return: None
        """
        claims = dict()
        if 'claims' in self.wd_json_representation:
            claims = self.wd_json_representation['claims']

        value_is_item = False

        for wd_property in self.data:
            if wd_property_store.wd_properties[wd_property]['datatype'] == 'item':
                claim_template = {
                    'mainsnak': {
                        'snaktype': 'value',
                        'property': wd_property,
                        'datatype': 'wikibase-item',
                        'datavalue': {
                            'value': {
                                'entity-type': 'item',
                                'numeric-id': ''
                            },
                            'type': 'wikibase-entityid'
                        },
                        'type': 'statement',
                        'rank': 'normal'
                    }
                }
                value_is_item = True

            elif wd_property_store.wd_properties[wd_property]['datatype'] == 'string':
                claim_template = {
                    'mainsnak': {
                        'snaktype': 'value',
                        'property': wd_property,
                        'datatype': 'string',
                        'datavalue': {
                            'value': '',
                            'type': 'string'
                        },
                        'type': 'statement',
                        'rank': 'normal'
                    }
                }
                value_is_item = False

            # search for statements which have already the correct value
            values_present = []
            if wd_property in claims:
                for i in claims[wd_property]:
                    current_value = ''

                    if value_is_item:
                        current_value = i['mainsnak']['datavalue']['value']['numeric-id']
                    elif not value_is_item:
                        current_value = i['mainsnak']['datavalue']['value']

                    if current_value in self.data[wd_property]:
                        values_present.append(current_value)
            else:
                # if not in claims, initialize new property
                claims[wd_property] = []

            # for appending and new claims, just append to the existing claims
            if wd_property in self.append_value:
                for value in self.data[wd_property]:
                    if value in values_present:
                        continue
                    else:
                        ct = copy.deepcopy(claim_template)
                        if value_is_item:
                            ct['mainsnak']['datavalue']['value']['numeric-id'] = value.upper().replace('Q', '')
                        elif not value_is_item:
                            ct['mainsnak']['datavalue']['value'] = value

                        claims[wd_property].append(ct)
            else:
                # set all claims for removal, except those where the values are already correct
                for x in range(0, len(claims[wd_property])):
                    if value_is_item:
                        value = claims[wd_property][x]['mainsnak']['datavalue']['value']['numeric-id']
                    elif not value_is_item:
                        value = claims[wd_property][x]['mainsnak']['datavalue']['value']

                    if value not in values_present:
                        claims[wd_property][x].update({'remove': ''})
                    else:
                        values_present.remove(value)
                        self.data[wd_property].remove(value)

                # add new claims for remaining values (could also be implemented in a way that old claims are recycled)
                for x in self.data[wd_property]:
                    ct = copy.deepcopy(claim_template)
                    if value_is_item:
                        ct['mainsnak']['datavalue']['value']['numeric-id'] = x.upper().replace('Q', '')
                    elif not value_is_item:
                        ct['mainsnak']['datavalue']['value'] = x

                    claims[wd_property].append(ct)

    def getClaims(self, claimProperty):
        """
        Returns all property values in a given wdItem
        :param wdItem: QID for a given WD item
        :param claimProperty: WD Property ID
        :return: a Python JSON representation of the requested WD item claim.
        """
        query = 'https://{}/w/api.php?action=wbgetclaims{}{}'.format(
            self.server,
            # '&entity=' + wdItem.getID(), BUG!!!!!! wdItem does not exist any more, as parameter has been removed
            'property' + claimProperty
        )

        return(json.load(urllib.urlopen(query)))

    def countPropertyValues(self, wdItem, claimProperty):
        """
        Count the number of claims with a given property
        :param wdItem:
        :param claimProperty:
        :return: the number of properties a certain claim has.
        """
        data = self.getClaims(wdItem, claimProperty)
        return len(data["claims"][claimProperty])

    def add_property(self, property):
        """
        :param property: takes a property the WDItem should have
        :return: None
        """
        pass

    def add_reference(self, wd_property, value, reference_types, reference_items, timestamp=False, overwrite=False):
        """
        Call this method to add a reference to a statement
        :param wd_property: the Wikidata property number a reference should be added to
        :param value: The value of a property the reference should be attached to
        :param reference_types: A list with reference property number strings (e.g. ['P248', 'P143'] stated in (P248),
                imported from (P143)) in the correct order they should be added to the claim
        :param reference_items: a list with item  strings the reference types should point to
        :param timestamp: Flag to add an optional timestamp as a reference. Default: False
        :param overwrite: Flag, set True if previous references for a property should be deleted
        :return: None
        """
        element_index = 0
        for i, sub_statement in enumerate(self.wd_json_representation['claims'][wd_property]):
            if sub_statement['mainsnak']['datatype'] == 'wikibase-item':
                if sub_statement['mainsnak']['datavalue']['value']['numeric-id'] == value.upper().replace('Q', ''):
                    element_index = i
            elif sub_statement['mainsnak']['datatype'] == 'string':
                if sub_statement['mainsnak']['datavalue']['value'] == value:
                    element_index = i

        references = []

        # Do not overwrite existing references unless specifically requested
        if (not overwrite) and 'references' in self.wd_json_representation['claims'][wd_property][element_index]['references']:
            references = self.wd_json_representation['claims'][wd_property][element_index]['references']
        else:
            self.wd_json_representation['claims'][wd_property][element_index]['references'] = references

        snaks = {}
        for i in reference_types:
            snak = dict()
            snak['property'] = i
            snak['snaktype'] = 'value'
            snak['datatype'] = 'wikibase-item'
            snak['datavalue'] = dict()
            snak['datavalue']['type'] = 'wikibase-entityid'
            snak['datavalue']['value'] = dict()
            snak['datavalue']['value']['entity-type'] = 'item'
            snak['datavalue']['value']['numeric-id'] = reference_items[reference_types.index(i)].upper().replace('Q', '')

            snaks[i] = [snak]

        # if required, create timestamp element
        if timestamp:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('+0000000%Y-%m-%dT00:00:00Z')
            wdTimestamp = dict()
            wdTimestamp['datatype'] = 'time'
            wdTimestamp['property'] = 'P813'
            wdTimestamp['snaktype'] = 'value'
            wdTimestamp['datavalue'] = dict()
            wdTimestamp['datavalue']['type'] = 'time'
            wdTimestamp['datavalue']['value'] = dict()
            wdTimestamp['datavalue']['value']['after'] = 0
            wdTimestamp['datavalue']['value']['before'] = 0
            wdTimestamp['datavalue']['value']['calendarmodel'] = 'http://www.wikidata.org/entity/Q1985727'
            wdTimestamp['datavalue']['value']['precision'] = 11
            wdTimestamp['datavalue']['value']['time'] = timestamp
            wdTimestamp['datavalue']['value']['timezone'] = 0

            snaks['P813'] = wdTimestamp

        snak_order = reference_types
        if timestamp:
            snak_order.append('P813')

        # add snacks and snack order to claims
        references.append({'snaks': snaks, 'snak-order': snak_order})

    def get_wd_json_representation(self):
        """
        A method to access the internal json representation of the WD item, mainly for testing
        :return: returns a Python json representation object of the WD item at the current state of the instance
        """
        return(self.wd_json_representation)

    def autoadd_references(self, refernce_type, reference_item):

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

    def set_label(self, label, lang='en'):
        """
        set the label for a WD item
        :param label: a label string as the wikidata item.
        :param lang: The language a description should be set for
        :return: None
        """
        self.wd_json_representation['labels'][lang] = {
            'language': lang,
            'value': label
        }

    def set_aliases(self, aliases, lang='en', append=True):
        """
        set the aliases for a WD item
        :param aliases: a list of strings representing the aliases of a WD item
        :param lang: The language a description should be set for
        :param append: If true, append a new alias to the list of existing aliases, else, overwrite. Default: True
        :return: None
        """

        current_aliases = set(self.wd_json_representation['aliases'][lang])
        if append:
            current_aliases.update(aliases)
        else:
            current_aliases = aliases

        self.wd_json_representation['aliases'][lang] = []
        for i in current_aliases:
            self.wd_json_representation['aliases'][lang].append({
                'language': lang,
                'value': i
            })

    def set_description(self, description, lang='en'):
        """
        Set the description for a WD item in a certain language
        :param description: The description of the item in a certain language
        :param lang: The language a description should be set for. Datatype: String
        :return: None
        """
        self.wd_json_representation['descriptions'][lang] = {
            'language': lang,
            'value': description
        }

    def write(self):
        """
        function to initiate writing the item data in the instance to Wikidata
        :return:
        """
        base_url = 'https://' + self.server + '/w/api.php?action=wbeditentity'

        if self.create_new_item:
            item_string = '&new=item'
        else:
            item_string = '&id=' + self.wd_item_id
    
        base_url += item_string
        base_url += '&data={{{}}}'.format(json.dumps(json.loads(self.wd_json_representation)["entities"][self.wd_item_id]))
        base_url += '&token={}'.format(self.token)

        try:
            print(base_url)
            # urllib2.urlopen(base_url_string)
        except urllib3.exceptions.HTTPError as e:
            PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
            print(e)





class IDMissingError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class WDSearchError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)

class ManualInterventionReqException(Exception):
    def __init__(self, value, property_string, item_list):
        self.value = value + ' Property: {}, items affected: {}'.format(property_string, item_list)

    def __str__(self):
        return repr(self.value)


#!usr/bin/env python
# -*- coding: utf-8 -*-

"""
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
"""

__author__ = 'Sebastian Burgstaller, Andra Waagmeester'
__license__ = 'GPL'

import time
import datetime
import itertools
import requests
import re

import PBB_Debug
import PBB_settings
import mysql.connector
import socket
import getpass
import copy
import pprint
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
        print(self.bot)
        print(self.start_date)
        print(self.finish_date)
        print(cursor.execute(sql_tuple, data_tuple))
        cnx.commit()
        
        # print all the first cell of all the rows
        # Use all the SQL you like
        cursor.execute("SELECT * FROM PBB_History")
        for row in cursor.fetchall() :
            print(row[0])


class WDItemList(object):
    def __init__(self, wdquery, wdprop=""):
        self.wdquery = wdquery
        self.wditems = self.getItemsByProperty(wdquery, wdprop)

    def getItemsByProperty(self, wdquery, wdproperty):
        """
        Gets all WikiData item IDs that contains statements containing property wdproperty
        :param wdquery: A string representation of a WD query
        :return: A Python json representation object with the search results is returned
        """
        url = 'http://wdq.wmflabs.org/api'
        params = {
            'q': wdquery,
            'props': wdproperty
        }

        reply = requests.get(url, params=params)

        return reply.json()


class WDItemEngine(object):

    wd_item_id = ''
    item_name = ''
    domain = ''
    create_new_item = False
    data = {}
    append_value = []

    # a list with all properties an item should have and/or modify
    property_list = {}
    wd_json_representation = {}

    def __init__(self, wd_item_id='', item_name='', domain='', data={}, server='www.wikidata.org',
                 append_value=[], references={}):
        """
        constructor
        :param wd_item_id: Wikidata item id
        :param item_name: Label of the wikidata item
        :param domain: string which tells the data domain the class should operate in
        :param data: a dictionary with WD property strings as keys and the data which should be written to
        a WD item as the property values
        :param append_value: a list of properties where potential existing values should not be overwritten by the data
        passed in the :parameter data.
        """
        self.wd_item_id = wd_item_id
        self.item_name = item_name
        self.domain = domain
        self.data = data
        self.server = server
        self.append_value = append_value
        self.references = references

        self.property_list = self.get_property_list()
        self.get_item_data(item_name, wd_item_id)

        self.__construct_claim_json()
        self.__append_references()

        if 'labels' not in self.wd_json_representation and item_name != '':
            self.set_label(label=item_name, lang='en')

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
                qids_by_props = self.__select_wd_item()

            if qids_by_props is not '':
                self.wd_item_id = 'Q{}'.format(qids_by_props)
                self.wd_json_representation = self.get_wd_entity(self.wd_item_id)
                self.__check_integrity()

    def get_wd_entity(self, item=''):
        """
        retrieve a WD item in json representation from Wikidata
        :param item: string which represents the wikidata QID
        :return: python complex dictionary represenation of a json
        """
        try:
            url = 'https://{}/w/api.php'.format(self.server)
            params = {
                'action': 'wbgetentities',
                'sites': 'enwiki',
                # 'languages': 'en',
                'ids': item,
                'format': 'json'
            }

            reply = requests.get(url, params=params)

            wd_reply = reply.json()['entities'][self.wd_item_id]
            wd_reply = {x: wd_reply[x] for x in (u'labels', u'descriptions', u'claims', u'aliases', u'sitelinks') if x in wd_reply}

            return(wd_reply)

        except requests.HTTPError as e:
            PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
            print(e)

    def get_wd_search_results(self, search_string=''):
        """
        Performs a search in WD for a certain WD search string
        :param search_string: a string which should be searched for in WD
        :return: returns a list of QIDs found in the search and a list of labels complementary to the QIDs
        """
        try:
            url = 'https://{}/w/api.php'.format(self.server)
            params = {
                'action': 'wbsearchentities',
                'language': 'en',
                'search': search_string,
                'format': 'json'
            }

            reply = requests.get(url, params=params)
            search_results = json.loads(reply.text)

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

        except requests.HTTPError as e:
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
        conflict_source = {}
        for wd_property in self.data:
            if wd_property in wd_property_store.wd_properties:
                try:
                    # check if the property is a core_id and should be unique for every WD item
                    if wd_property_store.wd_properties[wd_property]['core_id'] == 'True':
                        for data_point in self.data[wd_property]:
                            url = 'http://wdq.wmflabs.org/api'
                            params = {
                                'q': u'string[{}:{}]'.format(str(wd_property.replace('P', '')),
                                                             u'"{}"'.format(data_point)),
                            }

                            reply = requests.get(url, params=params)

                            tmp_qids = json.loads(reply.text)['items']
                            qid_list.append(tmp_qids)

                            # Protocol in what property the conflict arises
                            if wd_property in conflict_source:
                                conflict_source[wd_property].append(tmp_qids)
                            else:
                                conflict_source[wd_property] = [tmp_qids]

                            if len(tmp_qids) > 1:
                                raise ManualInterventionReqException(
                                    'More than one WD item has the same property value', wd_property, tmp_qids)

                except requests.HTTPError as e:
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
            raise ManualInterventionReqException('More than one WD item has the same property value',
                                                 conflict_source, unique_qids)
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
        else:
            self.wd_json_representation['claims'] = claims

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
                        }
                    },
                    'type': 'statement',
                    'rank': 'normal'
                }
                value_is_item = True
                self.data[wd_property] = [int(re.sub('[Qq]', '', x)) for x in self.data[wd_property]]

            elif wd_property_store.wd_properties[wd_property]['datatype'] == 'string':
                claim_template = {
                    'mainsnak': {
                        'snaktype': 'value',
                        'property': wd_property,
                        'datatype': 'string',
                        'datavalue': {
                            'value': '',
                            'type': 'string'
                        }
                    },
                    'type': 'statement',
                    'rank': 'normal'
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
                            ct['mainsnak']['datavalue']['value']['numeric-id'] = value
                        elif not value_is_item:
                            ct['mainsnak']['datavalue']['value'] = value

                        claims[wd_property].append(ct)
            else:
                # set all claims for removal, except those where the values are already correct
                loc_data = copy.deepcopy(self.data)
                for x in range(0, len(claims[wd_property])):
                    if value_is_item:
                        value = claims[wd_property][x]['mainsnak']['datavalue']['value']['numeric-id']
                    elif not value_is_item:
                        value = claims[wd_property][x]['mainsnak']['datavalue']['value']

                    # Remove value if not in self.data.
                    # If the value list in self.data[property] has no values at all, remove the whole claim
                    if value not in values_present or (len(self.data[wd_property]) == 0 and not self.create_new_item):
                        claims[wd_property][x].update({'remove': ''})
                    else:
                        values_present.remove(value)
                        loc_data[wd_property].remove(value)

                # add new claims for remaining values (could also be implemented in a way that old claims are recycled)
                for x in loc_data[wd_property]:
                    ct = copy.deepcopy(claim_template)
                    if value_is_item:
                        ct['mainsnak']['datavalue']['value']['numeric-id'] = x
                    elif not value_is_item:
                        ct['mainsnak']['datavalue']['value'] = x

                    claims[wd_property].append(ct)

    def __append_references(self):
        """
        Adds references using the self.references dictionary passed in the constructor. The references in self.reference[property]
        map to the values in self.data[property], therefore, the length of both lists MUST be equal. In other words,
        if for a property references should be added, reference values for all property values are required.
        If a timestamp should be added, the string 'TIMESTAMP' is reqired as the last element in the 'values' list
        :return:
        """

        # TODO: introduce a reference data check here!

        for wd_property in self.references:
            for count, ref in enumerate(self.references[wd_property]):
                timestamp = False
                if 'TIMESTAMP' in ref['ref_values']:
                    timestamp = True             
                    ref['ref_properties'].pop(ref['ref_values'].index('TIMESTAMP'))
                    ref['ref_values'].remove('TIMESTAMP')

                self.add_reference(wd_property=wd_property, value=self.data[wd_property][count], reference_types=ref['ref_properties'],
                                   reference_items=ref['ref_values'], timestamp=timestamp, overwrite=True)

    # TODO: Is this method needed anymore? It seems completely dysfunctional!!
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

        return requests.get(query).json()

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
                if sub_statement['mainsnak']['datavalue']['value']['numeric-id'] == value:
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
            snak[u'property'] = i
            snak[u'snaktype'] = u'value'
            snak[u'datatype'] = u'wikibase-item'
            snak[u'datavalue'] = dict()
            snak[u'datavalue'][u'type'] = u'wikibase-entityid'
            snak[u'datavalue'][u'value'] = dict()
            snak[u'datavalue'][u'value'][u'entity-type'] = u'item'
            snak[u'datavalue'][u'value'][u'numeric-id'] = int(reference_items[reference_types.index(i)].upper().replace('Q', ''))

            snaks[i] = [snak]

        # if required, create timestamp element
        if timestamp:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('+%Y-%m-%dT00:00:00Z')
            wdTimestamp = dict()
            wdTimestamp[u'datatype'] = u'time'
            wdTimestamp[u'property'] = u'P813'
            wdTimestamp[u'snaktype'] = u'value'
            wdTimestamp[u'datavalue'] = dict()
            wdTimestamp[u'datavalue'][u'type'] = u'time'
            wdTimestamp[u'datavalue'][u'value'] = dict()
            wdTimestamp[u'datavalue'][u'value'][u'after'] = 0
            wdTimestamp[u'datavalue'][u'value'][u'before'] = 0
            wdTimestamp[u'datavalue'][u'value'][u'calendarmodel'] = u'http://www.wikidata.org/entity/Q1985727'
            wdTimestamp[u'datavalue'][u'value'][u'precision'] = 11
            wdTimestamp[u'datavalue'][u'value'][u'time'] = timestamp
            wdTimestamp[u'datavalue'][u'value'][u'timezone'] = 0

            snaks[u'P813'] = [wdTimestamp]

        snak_order = copy.deepcopy(reference_types)
        if timestamp:
            snak_order.append(u'P813')

        # add snacks and snack order to claims
        references.append({'snaks': snaks, 'snaks-order': snak_order})

    def get_wd_json_representation(self):
        """
        A method to access the internal json representation of the WD item, mainly for testing
        :return: returns a Python json representation object of the WD item at the current state of the instance
        """
        return(self.wd_json_representation)

    def __check_integrity(self):
        """
        A method to check if when invoking __select_wd_item() and the WD item does not exist yet, but another item
        has a property of the current domain with a value like submitted in the data dict, this item does not get
        selected but a ManualInterventionReqException() is raised.
        :return: boolean True if test passed
        """
        # get all claim values for the currently loaded QID
        claim_values = dict()
        for key, value in self.wd_json_representation['claims'].items():
            claim_values[key] = list()
            for data_json in value:
                if data_json['mainsnak']['datatype'] == 'wikibase-item':
                    claim_values[key].append('Q{}'.format(data_json['mainsnak']['datavalue']['value']['numeric-id']))
                elif data_json['mainsnak']['datatype'] == 'string':
                    claim_values[key].append(data_json['mainsnak']['datavalue']['value'])

        # compare the claim values of the currently loaded QIDs to the data provided in self.data
        count_existing_ids = 0
        for i in self.data:
            if i in wd_property_store.wd_properties:
                count_existing_ids += 1

        data_match_count = 0
        for key, value_list in self.data.items():
            if key in claim_values:
                if len(set(value_list).intersection(set(claim_values[key]))) != 0:
                    data_match_count += 1

        # collect all names and aliases in English and German
        names = list()

        if 'labels' in self.wd_json_representation:
            for lang in self.wd_json_representation['labels']:
                if lang == 'en' or lang == 'de':
                    names.append(self.wd_json_representation['labels'][lang]['value'])

        if 'aliases' in self.wd_json_representation:
            for lang in self.wd_json_representation['aliases']:
                if lang == 'en' or lang == 'de':
                    for alias in self.wd_json_representation['aliases'][lang]:
                        names.append(alias['value'])

        names = [x.lower() for x in names]

        # make decision if ManualInterventionReqException should be raised.
        if data_match_count < (count_existing_ids - data_match_count) and self.item_name.lower() not in names:
            raise ManualInterventionReqException('Retrieved name does not match provided item name or core IDs. '
                                                 'Matching count {}, nonmatching count {}'
                                                 .format(data_match_count, count_existing_ids - data_match_count), '', '')
        else:
            return True

    def set_rank(self, prop, prop_value, rank):
        """
        sets the rank of a certain claim
        :param prop: the property number
        :type prop: str
        :param prop_value: the value of the claim, so the rank can be set for the correct value
        :type prop_value: str
        :param rank: the rank
        :type rank: str with one of three possible values: 'preferred', 'normal' or 'deprecated'
        :return:
        """
        valid_ranks = ['preferred', 'normal', 'deprecated']

        if rank not in valid_ranks:
            raise ValueError('No valid rank provided')

        if prop in self.wd_json_representation:
            for claim in self.wd_json_representation[prop]:
                dtype = claim['mainsnak']['datatype']
                value = ''
                if dtype == 'string':
                    value = claim['mainsnak']['datavalue']['value']
                elif dtype == 'wikibase-item':
                    value = str(claim['mainsnak']['datavalue']['value']['numeric-id'])
                    prop_value = prop_value.lstrip('Q')

                if prop_value == value:
                    claim['rank'] = rank

    def set_label(self, label, lang='en'):
        """
        Set the label for a WD item in a certain language
        :param label: The description of the item in a certain language
        :type label: str
        :param lang: The language a label should be set for.
        :type lang: str
        :return: None
        """
        if 'labels' not in self.wd_json_representation:
            self.wd_json_representation['labels'] = {}
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
        if 'aliases' not in self.wd_json_representation:
            self.wd_json_representation['aliases'] = {}

        if not append or lang not in self.wd_json_representation['aliases']:
            self.wd_json_representation['aliases'][lang] = []

        for alias in aliases:
            found = False
            for current_aliases in self.wd_json_representation['aliases'][lang]:
                if alias != current_aliases['value']:
                    continue
                else:
                    found = True
                    break

            if not found:
                self.wd_json_representation['aliases'][lang].append({
                    'language': lang,
                    'value': alias
                })

    def set_description(self, description, lang='en'):
        """
        Set the description for a WD item in a certain language
        :param description: The description of the item in a certain language
        :type description: str
        :param lang: The language a description should be set for.
        :type lang: str
        :return: None
        """
        if 'descriptions' not in self.wd_json_representation:
            self.wd_json_representation['descriptions'] = {}
        self.wd_json_representation['descriptions'][lang] = {
            'language': lang,
            'value': description
        }

    def set_sitelink(self, site, title):
        """
        Set sitelinks to corresponding Wikipedia pages
        :param site: The Wikipedia page a sitelink is directed to (e.g. 'enwiki')
        :param title: The title of the Wikipedia page the sitelink is directed to
        :return:
        """
        if 'sitelinks' not in self.wd_json_representation:
            self.wd_json_representation['sitelinks'] = {}

        self.wd_json_representation['sitelinks'][site] = {
            'site': site,
            'title': title
        }

    def write(self, login):
        """
        function to initiate writing the item data in the instance to Wikidata
        :param login: a instance of the class PBB_login which provides edit-cookies and edit-tokens
        :return: None
        """
        cookies = login.get_edit_cookie()
        edit_token = login.get_edit_token()

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }
        payload = {
            u'action': u'wbeditentity',
            # u'data': json.dumps(self.wd_json_representation, encoding='utf-8'),
            u'data': json.JSONEncoder(encoding='utf-8').encode(self.wd_json_representation),
            u'format': u'json',
            u'token': edit_token
        }

        if self.create_new_item:
            payload.update({u'new': u'item'})
        else:
            payload.update({u'id': self.wd_item_id})

        base_url = 'https://' + self.server + '/w/api.php'

        try:
            reply = requests.post(base_url, headers=headers, data=payload, cookies=cookies)

            json_data = json.loads(reply.text)
            pprint.pprint(json_data)
            if 'error' in json_data.keys():
                raise UserWarning("Wikidata api returns error: "+json_data['error']['info'])
        except (requests.HTTPError, UserWarning) as e: 
            repr(e)
            PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())

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


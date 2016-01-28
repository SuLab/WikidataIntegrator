#!usr/bin/env python
# -*- coding: utf-8 -*-

import time
import datetime
import itertools
import requests
import re
import logging
import os

import copy
import pprint
import wd_property_store
import json

from SPARQLWrapper import SPARQLWrapper, JSON

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

    log_file_name = ''

    def __init__(self, wd_item_id='', item_name='', domain='', data=None, server='www.wikidata.org',
                 append_value=None, use_sparql=True):
        """
        constructor
        :param wd_item_id: Wikidata item id
        :param item_name: Label of the wikidata item
        :param domain: The data domain the class should operate in. If None and item_name not '', create new item from scratch.
        :type domain: str or None
        :param data: a dictionary with WD property strings as keys and the data which should be written to
        a WD item as the property values
        :param append_value: a list of properties where potential existing values should not be overwritten by the data
        passed in the :parameter data.
        """
        self.wd_json_representation = {}
        self.wd_item_id = wd_item_id
        self.item_name = item_name
        self.create_new_item = False
        self.domain = domain
        self.server = server
        self.use_sparql = use_sparql
        self.statements = []
        self.entity_metadata = {}

        if data is None:
            self.data = []
        else:
            self.data = data

        if append_value is None:
            self.append_value = []
        else:
            self.append_value = append_value

        if self.item_name is not '' and self.domain is None and len(self.data) > 0:
            self.create_new_item = True
        elif self.item_name is '' and self.wd_item_id is '':
            raise IDMissingError('No item name or WD identifier was given')
        elif self.wd_item_id is not '':
            self.wd_json_representation = self.get_wd_entity()
        else:
            if self.domain is None or self.domain == '':
                raise ValueError('Domain parameter has not been set')
            try:
                # qids_by_string_search = self.get_wd_search_results(item_name)
                qids_by_props = self.__select_wd_item()

            except WDSearchError as e:
                self.log('ERROR', str(e))
                qids_by_props = self.__select_wd_item()

            if qids_by_props is not '':
                self.wd_item_id = 'Q{}'.format(qids_by_props)
                self.wd_json_representation = self.get_wd_entity()
                self.__check_integrity()

        self.__construct_claim_json()

        if ('labels' not in self.wd_json_representation or 'en' not in self.wd_json_representation['labels']) \
                and item_name != '':
            self.set_label(label=item_name, lang='en')

    def get_wd_entity(self):
        """
        retrieve a WD item in json representation from Wikidata
        :rtype: dict
        :return: python complex dictionary represenation of a json
        """
        try:
            url = 'https://{}/w/api.php'.format(self.server)
            params = {
                'action': 'wbgetentities',
                'sites': 'enwiki',
                'ids': self.wd_item_id,
                'format': 'json'
            }

            reply = requests.get(url, params=params)

            return self.parse_wd_json(wd_json=reply.json()['entities'][self.wd_item_id])

        except requests.HTTPError as e:
            self.log('ERROR', str(e))

    def parse_wd_json(self, wd_json):
        """
        Parses a WD entity json and generates the datatype objects, sets self.wd_json_representation
        :param wd_json: the json of a WD entity
        :type wd_json: A Python Json representation of a WD item
        :return: returns the json representation containing 'labels', 'descriptions', 'claims', 'aliases', 'sitelinks'.
        """
        wd_data = {x: wd_json[x] for x in ('labels', 'descriptions', 'claims', 'aliases', 'sitelinks') if x in wd_json}
        self.entity_metadata = {x: wd_json[x] for x in wd_json if x not in
                                ('labels', 'descriptions', 'claims', 'aliases', 'sitelinks')}

        self.statements = []
        for prop in wd_data['claims']:
            for z in wd_data['claims'][prop]:
                data_type = [x for x in WDBaseDataType.__subclasses__() if x.DTYPE == z['mainsnak']['datatype']][0]
                statement = data_type.from_json(z)
                self.statements.append(statement)

        self.wd_json_representation = wd_data

        return wd_data

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
                return []
            else:
                id_list = []
                id_labels = []
                for i in search_results['search']:
                    id_list.append(i['id'])
                    id_labels.append(i['label'])

                return id_list

        except requests.HTTPError as e:
            self.log('ERROR', str(e))

    def get_property_list(self):
        """
        List of properties on the current item
        :return: a list of WD property ID strings (Pxxxx).
        """
        property_list = set()
        for x in self.statements:
            property_list.add(x.get_prop_nr())

        return list(property_list)

    def __select_wd_item(self):
        """
        The most likely WD item QID should be returned, after querying WDQ for all values in core_id properties
        :return: Either a single WD QID is returned, or an empty string if no suitable item in WD
        """
        qid_list = []
        conflict_source = {}
        for statement in self.data:
            wd_property = statement.get_prop_nr()

            # TODO: implement special treatment when searching for date/coordinate values
            data_point = statement.get_value()
            if isinstance(data_point, tuple):
                data_point = data_point[0]

            if wd_property in wd_property_store.wd_properties:
                try:
                    # check if the property is a core_id and should be unique for every WD item
                    if wd_property_store.wd_properties[wd_property]['core_id'] == 'True':
                        tmp_qids = []

                        if not self.use_sparql:
                            url = 'http://wdq.wmflabs.org/api'
                            params = {
                                'q': u'string[{}:{}]'.format(str(wd_property).replace('P', ''),
                                                             u'"{}"'.format(data_point)),
                            }

                            reply = requests.get(url, params=params)

                            tmp_qids = reply.json()['items']
                        else:
                            query = statement.sparql_query.format(wd_property, data_point)
                            results = WDItemEngine.execute_sparql_query(query=query)

                            for i in results['results']['bindings']:
                                qid = i['item_id']['value'].split('/')[-1]
                                # remove 'Q' prefix
                                qid = qid[1:]
                                tmp_qids.append(qid)

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
                    self.log('ERROR', str(e))

        qid_list = [i for i in itertools.chain.from_iterable(qid_list)]

        if len(qid_list) == 0:
            self.create_new_item = True
            return ''

        print(qid_list)

        unique_qids = set(qid_list)
        if len(unique_qids) > 1:
            raise ManualInterventionReqException('More than one WD item has the same property value',
                                                 conflict_source, unique_qids)
        elif len(unique_qids) == 1:
            return list(unique_qids)[0]

    def __construct_claim_json(self):
        """
        Writes the properties from self.data to a new or existing json in self.wd_json_representation
        :return: None
        """

        def handle_references(old_item, new_item):
            """
            Local function to handle updating of references. Has the following behavior: If overwrite_references in
            a provided data type is set to TRUE or an existing item does not have references, just overwrite existing
            refs. Else: Check if P248 exists and do not overwrite those refs. Only overwrite, if value of P248 and
            value of the DB entry match. Overwrite all other refs without P248.
            :param old_item: An item containing the data as currently in WD
            :type old_item: A child of WDBaseDataType
            :param new_item: An item containing the new data which should be written to WD
            :type new_item: A child of WDBaseDataType
            """
            ref_properties = ['P248', 'P1476', 'P407', 'P813', 'P143']
            new_references = copy.deepcopy(new_item.get_references())
            existing_references = copy.deepcopy(old_item.get_references())

            if True in [z.overwrite_references for y in new_references for z in y] \
                    or sum(map(lambda z: len(z), existing_references)) == 0:
                old_item.set_references(new_item.get_references())

            elif 'P248' in [z.get_prop_nr() for y in new_references for z in y]:
                for count, ref_block in enumerate(old_item.get_references()):
                    for new_ref_block in copy.copy(new_references):
                        db_value_prop = ''
                        match_dict = {}
                        for ref in ref_block:
                            for new_ref in new_ref_block:
                                if ref == new_ref:
                                    cur_prop = new_ref.get_prop_nr()
                                    match_dict.update({cur_prop: True})
                                    if cur_prop in wd_property_store.wd_properties and cur_prop not in ref_properties:
                                        db_value_prop = cur_prop

                        if db_value_prop in match_dict or 'P143' in match_dict:
                            existing_references[count] = new_ref_block
                            new_references.remove(new_ref_block)

                # remove all references without 'stated in'
                drop_refs = []
                for ref in existing_references:
                    prop_nr_list = [z.get_prop_nr() for z in ref]

                    if 'P248' not in prop_nr_list:
                        drop_refs.append(ref)

                while len(drop_refs) > 0:
                    existing_references.remove(drop_refs.pop())

                if len(new_references) > 0:
                    for uu in new_references:
                        existing_references.append(uu)
                old_item.set_references(existing_references)

        # sort the incoming data according to the WD property number
        self.data.sort(key=lambda z: z.get_prop_nr().lower())

        # collect all statements which should be deleted
        statements_for_deletion = []
        for item in self.data:
            if item.get_value() == '' and isinstance(item, WDBaseDataType):
                statements_for_deletion.append(item.get_prop_nr())

        if self.create_new_item:
            self.statements = copy.copy(self.data)
        else:
            for stat in self.data:
                prop_nr = stat.get_prop_nr()

                prop_data = [x for x in self.statements if x.get_prop_nr() == prop_nr]
                prop_pos = [True if x.get_prop_nr() == prop_nr else False for x in self.statements]
                prop_pos.reverse()
                insert_pos = len(prop_pos) - (prop_pos.index(True) if True in prop_pos else 0)

                # If value should be appended, check if values exists, if not, append
                if prop_nr in self.append_value:
                    equal_items = [True if stat == x else False for x in prop_data]
                    if True not in equal_items:
                        self.statements.insert(insert_pos + 1, stat)
                    else:
                        # if item exists, modify rank
                        current_item = prop_data[equal_items.index(True)]
                        current_item.set_rank(stat.get_rank())
                        handle_references(old_item=current_item, new_item=stat)
                    continue

                # set all existing values of a property for removal
                for x in prop_data:
                    # for deletion of single statements, do not set all others to delete
                    if hasattr(stat, 'remove'):
                        break
                    elif x.get_id() != '' and not hasattr(x, 'retain'):
                        setattr(x, 'remove', '')

                match = []
                for i in prop_data:
                    if stat == i and hasattr(stat, 'remove'):
                        match.append(True)
                        setattr(i, 'remove', '')
                    elif stat == i:
                        match.append(True)
                        setattr(i, 'retain', '')
                        delattr(i, 'remove')

                        handle_references(old_item=i, new_item=stat)

                        i.set_rank(rank=stat.get_rank())
                    # if there is no value, do not add an element, this is also used to delete whole properties.
                    elif i.get_value() != '':
                        match.append(False)

                if True not in match and not hasattr(stat, 'remove'):
                    self.statements.insert(insert_pos + 1, stat)

        # For whole property deletions, add remove flag to all statements which should be deleted
        for item in copy.deepcopy(self.statements):
            if item.get_prop_nr() in statements_for_deletion and item.get_id() != '':
                setattr(item, 'remove', '')
            elif item.get_prop_nr() in statements_for_deletion:
                self.statements.remove(item)

        # regenerate claim json
        self.wd_json_representation['claims'] = {}
        for stat in self.statements:
            prop_nr = stat.get_prop_nr()
            if prop_nr not in self.wd_json_representation['claims']:
                self.wd_json_representation['claims'][prop_nr] = []
            self.wd_json_representation['claims'][prop_nr].append(stat.get_json_representation())

    def get_wd_json_representation(self):
        """
        A method to access the internal json representation of the WD item, mainly for testing
        :return: returns a Python json representation object of the WD item at the current state of the instance
        """
        return self.wd_json_representation

    def __check_integrity(self):
        """
        A method to check if when invoking __select_wd_item() and the WD item does not exist yet, but another item
        has a property of the current domain with a value like submitted in the data dict, this item does not get
        selected but a ManualInterventionReqException() is raised. This check is dependent on the core identifiers
        of a certain domain.
        :return: boolean True if test passed
        """
        # generate a set containing all property number of the item currently loaded
        core_props_list = set([
            x.get_prop_nr()
            for x in self.statements if x.get_prop_nr() in wd_property_store.wd_properties and
            wd_property_store.wd_properties[x.get_prop_nr()]['core_id'] == 'True'
        ])

        # compare the claim values of the currently loaded QIDs to the data provided in self.data
        count_existing_ids = 0
        for i in self.data:
            prop_nr = i.get_prop_nr()
            if prop_nr in core_props_list:
                count_existing_ids += 1

        match_count_per_prop = dict()
        for new_stat in self.data:
            for stat in self.statements:
                pn = new_stat.get_prop_nr()
                if new_stat == stat and pn in core_props_list:
                    if pn in match_count_per_prop:
                        match_count_per_prop[pn] += 1
                    else:
                        match_count_per_prop[pn] = 1

        core_prop_match_count = 0
        for x in match_count_per_prop:
            if match_count_per_prop[x] > 0:
                core_prop_match_count += 1

        if core_prop_match_count < count_existing_ids * 0.66:
            raise ManualInterventionReqException('Retrieved item ({}) does not match provided core IDs. '
                                                 'Matching count {}, non-matching count {}'
                                                 .format(self.wd_item_id, core_prop_match_count,
                                                         count_existing_ids - core_prop_match_count), '', '')
        else:
            return True

    def get_label(self, lang='en'):
        """
        Retrurns the label for a certain language
        :param lang:
        :type lang: str
        :return: returns the label in the specified language, an empty string if the label does not exist
        """
        try:
            return self.wd_json_representation['labels'][lang]['value']
        except KeyError:
            return ''

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

    def get_aliases(self, lang='en'):
        """
        Retrieve the aliases in a certain language
        :param lang: The Wikidata language the description should be retrieved for
        :return: Returns a list of aliases, an empty list if none exist for the specified language
        """
        alias_list = []
        if 'aliases' in self.wd_json_representation and lang in self.wd_json_representation['aliases']:
            for alias in self.wd_json_representation['aliases'][lang]:
                alias_list.append(alias['value'])

        return alias_list

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
                if alias.lower() != current_aliases['value'].lower():
                    continue
                else:
                    found = True
                    break

            if not found:
                self.wd_json_representation['aliases'][lang].append({
                    'language': lang,
                    'value': alias
                })

    def get_description(self, lang='en'):
        """
        Retrieve the description in a certain language
        :param lang: The Wikidata language the description should be retrieved for
        :return: Returns the description string
        """
        if 'descriptions' not in self.wd_json_representation or lang not in self.wd_json_representation['descriptions']:
            return ''
        else:
            return self.wd_json_representation['descriptions'][lang]['value']

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

    def set_sitelink(self, site, title, badges=()):
        """
        Set sitelinks to corresponding Wikipedia pages
        :param site: The Wikipedia page a sitelink is directed to (e.g. 'enwiki')
        :param title: The title of the Wikipedia page the sitelink is directed to
        :param badges: An iterable containing Wikipedia badge strings.
        :return:
        """
        if 'sitelinks' not in self.wd_json_representation:
            self.wd_json_representation['sitelinks'] = {}

        self.wd_json_representation['sitelinks'][site] = {
            'site': site,
            'title': title,
            'badges': badges
        }

    def get_sitelink(self, site):
        """
        A method to access the interwiki links in the json.model
        :param site: The Wikipedia site the interwiki/sitelink should be returned for
        :return: The interwiki/sitelink string for the specified Wikipedia will be returned.
        """
        if "sitelinks" in self.wd_json_representation.keys():
            if site in self.wd_json_representation['sitelinks']:
                return self.wd_json_representation['sitelinks'][site]
            else:
                return None
        else:
            return None

    def write(self, login):
        """
        Writes the WD item Json to WD and after successful write, updates the object with new ids and hashes generated
        by WD. For new items, also returns the new QIDs.
        :param login: a instance of the class PBB_login which provides edit-cookies and edit-tokens
        :return: the WD QID on sucessful write
        """
        cookies = login.get_edit_cookie()
        edit_token = login.get_edit_token()

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }
        payload = {
            'action': 'wbeditentity',
            'data': json.JSONEncoder().encode(self.wd_json_representation),
            'format': 'json',
            'token': edit_token,
            'bot': ''
        }

        if self.create_new_item:
            payload.update({u'new': u'item'})
        else:
            payload.update({u'id': self.wd_item_id})

        base_url = 'https://' + self.server + '/w/api.php'

        try:
            reply = requests.post(base_url, headers=headers, data=payload, cookies=cookies)

            # if the server does not reply with a string which can be parsed into a json, an error will be raised.
            json_data = reply.json()

            # pprint.pprint(json_data)

            if 'error' in json_data.keys() and 'code' in json_data['error'] \
                    and json_data['error']['code'] == 'readonly':
                print('Wikidata currently is in readonly mode, waiting for 60 seconds')
                time.sleep(60)
                return self.write(login=login)

            if 'error' in json_data.keys() and 'messages' in json_data['error']:
                if 'wikibase-validator-label-with-description-conflict' == json_data['error']['messages'][0]['name']:
                    raise NonUniqueLabelDescriptionPairError(json_data)
                else:
                    raise WDApiError(json_data)
            elif 'error' in json_data.keys():
                raise WDApiError(json_data)

        except Exception as e:
            print('Error while writing to Wikidata')
            raise e

        # after successful write, update this object with latest json, QID and parsed data types.
        self.create_new_item = False
        self.wd_item_id = json_data['entity']['id']
        self.parse_wd_json(wd_json=json_data['entity'])

        return self.wd_item_id

    @staticmethod
    def log(level, message):
        """
        A static method which initiates log files compatible to .csv format, allowing for easy further analysis.
        :param level: The log level as in the Python logging documentation, 5 different possible values with increasing
         severity
        :type level: String of value 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'.
        :param message: The logging data which should be written to the log file. In order to achieve a csv-file
         compatible format, all fields must be separated by a colon. Furthermore, all strings which could contain
         colons, spaces or other special characters must be enclosed in double-quotes.
         e.g. '{main_data_id}, "{exception_type}", "{message}", {wd_id}, {duration}'.format(
                        main_data_id=<main_id>,
                        exception_type=<excpetion type>,
                        message=<exception message>,
                        wd_id=<wikidata id>,
                        duration=<duration of action>
        :type message: str
        """
        log_levels = {'DEBUG': logging.DEBUG, 'ERROR': logging.ERROR, 'INFO': logging.INFO, 'WARNING': logging.WARNING,
                      'CRITICAL': logging.CRITICAL}

        if not os.path.exists('./logs'):
            os.makedirs('./logs')

        logger = logging.getLogger('WD_logger')
        if WDItemEngine.log_file_name == '':
            WDItemEngine.log_file_name = './logs/WD_bot_run-{}.log'.format(time.strftime('%Y-%m-%d_%H:%M',
                                                                                         time.localtime()))
            logger.setLevel(logging.DEBUG)
            file_handler = logging.FileHandler(WDItemEngine.log_file_name)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter(fmt='%(levelname)s, %(asctime)s, %(message)s',
                                                        datefmt='%m/%d/%Y %H:%M:%S'))
            logger.addHandler(file_handler)

        logger.log(level=log_levels[level], msg=message)

    @staticmethod
    def execute_sparql_query(prefix='', query='', endpoint='https://query.wikidata.org/bigdata/namespace/wdq/sparql'):
        """
        Static method which can be used to execute any SPARQL query
        :param prefix: The URI prefixes required for an endpoint, default is the Wikidata specific prefixes
        :param query: The actual SPARQL query string
        :param endpoint: The URL string for the SPARQL endpoint. Default is the URL for the Wikidata SPARQL endpoint
        :return: The results of the query are returned in JSON format
        """

        # standard prefixes for the Wikidata SPARQL endpoint
        # PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#> has been removed for performance reasons
        wd_standard_prefix = '''
            PREFIX wd: <http://www.wikidata.org/entity/>
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wikibase: <http://wikiba.se/ontology#>
            PREFIX p: <http://www.wikidata.org/prop/>
            PREFIX v: <http://www.wikidata.org/prop/statement/>
            PREFIX q: <http://www.wikidata.org/prop/qualifier/>

        '''

        if prefix == '':
            prefix = wd_standard_prefix

        query_string = prefix + query

        sparql = SPARQLWrapper(endpoint)
        sparql.setQuery(query_string)
        sparql.setReturnFormat(JSON)

        return sparql.query().convert()

    @staticmethod
    def merge_items(from_id, to_id, login_obj, server='https://www.wikidata.org', ignore_conflicts=''):
        """
        A static method to merge two Wikidata items
        :param from_id: The QID which should be merged into another item
        :type from_id: string with 'Q' prefix
        :param to_id: The QID into which another item should be merged
        :type to_id: string with 'Q' prefix
        :param login_obj: The object containing the login credentials and cookies
        :type login_obj: instance of PBB_login.WDLogin
        :param server: The MediaWiki server which should be used, default: 'https://www.wikidata.org'
        :type server: str
        :param ignore_conflicts: A string with the values 'description', 'statement' or 'sitelink', separated
                by a pipe ('|') if using more than one of those.
        :type ignore_conflicts: str
        """
        url = server + '/w/api.php'

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }

        params = {
            'action': 'wbmergeitems',
            'fromid': from_id,
            'toid': to_id,
            'token': login_obj.get_edit_token(),
            'format': 'json',
            'bot': '',
            'ignoreconflicts': ignore_conflicts
        }

        try:
            merge_reply = requests.post(url=url, data=params, headers=headers, cookies=login_obj.get_edit_cookie())

            if 'error' in merge_reply.json():
                raise MergeError(merge_reply.json())

        except requests.HTTPError as e:
            print(e)
            return {'error': 'HTTPError'}

        return merge_reply.json()


class JsonParser(object):
    references = []
    qualifiers = []
    final = False
    current_type = None

    def __init__(self, f):
        self.f = f

    def __call__(self, *args):
        self.json_representation = args[1]

        if self.final:
            self.final = False
            return self.f(cls=self.current_type, jsn=self.json_representation)

        if 'mainsnak' in self.json_representation:
            self.mainsnak = None
            self.references = []
            self.qualifiers = []
            json_representation = self.json_representation

            if 'references' in json_representation:
                self.references.extend([[] for x in json_representation['references']])
                for count, ref_block in enumerate(json_representation['references']):
                    ref_hash = ''
                    if 'hash' in ref_block:
                        ref_hash = ref_block['hash']
                    for prop in ref_block['snaks-order']:
                        jsn = ref_block['snaks'][prop]

                        ref_class = self.get_class_representation(jsn[0])
                        ref_class.is_reference = True
                        ref_class.snak_type = jsn[0]['snaktype']
                        ref_class.set_hash(ref_hash)

                        self.references[count].append(ref_class)

                # print(self.references)
            if 'qualifiers' in json_representation:
                for prop in json_representation['qualifiers-order']:
                    qual = json_representation['qualifiers'][prop]
                    qual_hash = ''
                    if 'hash' in qual[0]:
                        qual_hash = qual[0]['hash']

                    qual_class = self.get_class_representation(qual[0])
                    qual_class.is_qualifier = True
                    qual_class.snak_type = qual[0]['snaktype']
                    qual_class.set_hash(qual_hash)
                    self.qualifiers.append(qual_class)

                # print(self.qualifiers)
            mainsnak = self.get_class_representation(json_representation['mainsnak'])
            mainsnak.set_references(self.references)
            mainsnak.set_qualifiers(self.qualifiers)
            if 'id' in json_representation:

                mainsnak.set_id(json_representation['id'])
            if 'rank' in json_representation:
                mainsnak.set_rank(json_representation['rank'])
            mainsnak.snak_type = json_representation['mainsnak']['snaktype']

            return mainsnak

        elif 'property' in self.json_representation:
            return self.get_class_representation(jsn=self.json_representation)

    def get_class_representation(self, jsn):
        data_type = [x for x in WDBaseDataType.__subclasses__() if x.DTYPE == jsn['datatype']][0]
        self.final = True
        self.current_type = data_type
        return data_type.from_json(jsn)


class WDBaseDataType(object):
    """
    The base class for all Wikidata data types, they inherit from it
    """

    sparql_query = '''
        SELECT * WHERE {{
            ?item_id wdt:{0} '{1}' .
        }}
    '''

    def __init__(self, value, snak_type, data_type, is_reference, is_qualifier, references, qualifiers, rank, prop_nr):
        """
        Constructor, will be called by all data types.
        :param value: Data value of the WD data snak
        :type value: str or int or tuple
        :param snak_type: The snak type of the WD data snak, three values possible, depending if the value is a
                            known (value), not existent (novalue) or unknown (somevalue). See WD documentation.
        :type snak_type: a str of either 'value', 'novalue' or 'somevalue'
        :param data_type: The WD data type declaration of this snak
        :type data_type: str
        :param is_reference: States if the snak is a reference, mutually exclusive with qualifier
        :type is_reference: boolean
        :param is_qualifier: States if the snak is a qualifier, mutually exlcusive with reference
        :type is_qualifier: boolean
        :param references: A one level nested list with reference WD snaks of base type WDBaseDataType, e.g.
                            references=[[<WDBaseDataType>, <WDBaseDataType>], [<WDBaseDataType>]]
                            This will create two references, the first one with two statements, the second with one
        :type references: A one level nested list with instances of WDBaseDataType or children of it.
        :param qualifiers: A list of qualifiers for the WD mainsnak
        :type qualifiers: A list with instances of WDBaseDataType or children of it.
        :param rank: The rank of a WD mainsnak, should determine the status of a value
        :type rank: A string of one of three allowed values: 'normal', 'deprecated', 'preferred'
        :param prop_nr: The WD property number a WD snak belongs to
        :type prop_nr: A string with a prefixed 'P' and several digits e.g. 'P715' (Drugbank ID)
        :return:
        """
        self.value = value
        self.snak_type = snak_type
        self.data_type = data_type
        self.references = references
        self.qualifiers = qualifiers
        self.is_reference = is_reference
        self.is_qualifier = is_qualifier
        self.rank = rank

        if type(prop_nr) is int:
            self.prop_nr = 'P' + str(prop_nr)
        elif prop_nr.startswith('P'):
            self.prop_nr = prop_nr
        else:
            self.prop_nr = 'P' + prop_nr

        # Flag to allow complete overwrite of existing references for a value
        self.overwrite_references = False

        # WD internal ID and hash are issued by the WD servers
        self.id = ''
        self.hash = ''

        self.json_representation = {
            "snaktype": self.snak_type,
            "property": self.prop_nr,
            "datavalue": {},
            "datatype": self.data_type
        }

        self.snak_types = ['value', 'novalue', 'somevalue']
        if snak_type not in self.snak_types:
            raise ValueError('{} is not a valid snak type'.format(snak_type))

        if self.is_qualifier and self.is_reference:
            raise ValueError('A claim cannot be a reference and a qualifer at the same time')
        if (len(references) > 0 or len(self.qualifiers) > 0) and (self.is_qualifier or self.is_reference):
            raise ValueError('Qualifiers or references cannot have references')

    def __eq__(self, other):
        # check if the qualifiers are equal
        equal_qualifiers = True
        self_qualifiers = copy.deepcopy(self.get_qualifiers())
        self_qualifiers.sort(key=lambda z: z.get_prop_nr().lower())

        other_qualifiers = copy.deepcopy(other.get_qualifiers())
        other_qualifiers.sort(key=lambda z: z.get_prop_nr().lower())

        if len(self_qualifiers) != len(other_qualifiers):
            equal_qualifiers = False

        else:
            for count, i in enumerate(self_qualifiers):
                if not i == other_qualifiers[count]:
                    equal_qualifiers = False

        if self.get_value() == other.get_value() and self.get_prop_nr() == other.get_prop_nr() and equal_qualifiers:
            return True
        else:
            return False

    def __ne__(self, other):
        if self.get_value() != other.get_value() or self.get_prop_nr() != other.get_prop_nr():
            return True
        else:
            return False

    def get_value(self):
        return self.value

    def set_value(self, value):
        if value is None or (self.snak_type == 'novalue' or self.snak_type == 'somevalue'):
            del self.json_representation['datavalue']
        elif 'datavalue' not in self.json_representation:
            self.json_representation['datavalue'] = {}

    def get_references(self):
        return self.references

    def set_references(self, references):
        if len(references) > 0 and (self.is_qualifier or self.is_reference):
            raise ValueError('Qualifiers or references cannot have references')

        self.references = references

    def get_qualifiers(self):
        return self.qualifiers

    def set_qualifiers(self, qualifiers):
        # TODO: introduce a check to prevent duplicate qualifiers, those are not allowed in WD
        if len(qualifiers) > 0 and (self.is_qualifier or self.is_reference):
            raise ValueError('Qualifiers or references cannot have references')

        self.qualifiers = qualifiers

    def get_rank(self):
        if self.is_qualifier or self.is_reference:
            return ''
        else:
            return self.rank

    def set_rank(self, rank):
        if self.is_qualifier or self.is_reference:
            raise ValueError('References or qualifiers do not have ranks')

        valid_ranks = ['normal', 'deprecated', 'preferred']

        if rank not in valid_ranks:
            raise ValueError('{} not a valid rank'.format(rank))

        self.rank = rank

    def get_id(self):
        return self.id

    def set_id(self, claim_id):
        self.id = claim_id

    def set_hash(self, wd_hash):
        self.hash = wd_hash

    def get_hash(self):
        return self.hash

    def get_prop_nr(self):
        return self.prop_nr

    def set_prop_nr(self, prop_nr):
        if prop_nr[0] != 'P':
            raise ValueError('Invalid property number')

        self.prop_nr = prop_nr

    def is_reference(self):
        return self.is_reference

    def is_qualifier(self):
        return self.is_qualifier

    def get_json_representation(self):
        if self.is_qualifier or self.is_reference:
            tmp_json = {
                self.prop_nr: [self.json_representation]
            }
            if self.hash != '' and self.is_qualifier:
                self.json_representation.update({'hash': self.hash})

            return tmp_json
        else:
            ref_json = []
            for count, ref in enumerate(self.references):
                snaks_order = []
                snaks = {}
                ref_json.append({
                    'snaks': snaks,
                    'snaks-order': snaks_order
                })
                for sub_ref in ref:
                    prop_nr = sub_ref.get_prop_nr()
                    # set the hash for the reference block
                    if sub_ref.get_hash() != '':
                        ref_json[count].update({'hash': sub_ref.get_hash()})
                    tmp_json = sub_ref.get_json_representation()

                    snaks.update(tmp_json)
                    snaks_order.append(prop_nr)

            qual_json = {}
            qualifiers_order = []
            for qual in self.qualifiers:
                qual_json.update(qual.get_json_representation())
                qualifiers_order.append(qual.get_prop_nr())

            statement = {
                'mainsnak': self.json_representation,
                'type': 'statement',
                'rank': self.rank,
                'qualifiers': qual_json,
                'qualifiers-order': qualifiers_order,
                'references': ref_json
            }
            if self.id != '':
                statement.update({'id': self.id})

            if hasattr(self, 'remove'):
                statement.update({'remove': ''})

            return statement

    @classmethod
    @JsonParser
    def from_json(cls, json_representation):
        pass

    @classmethod
    def delete_statement(cls, prop_nr):
        """
        This serves as an alternative constructor for WDBaseDataType with the only purpose of holding a WD property
        number and an empty string value in order to indicate that the whole statement with this property number of a
        WD item should be deleted.
        :param prop_nr: A WD property number as string
        :return: An instance of WDBaseDataType
        """
        return cls(value='', snak_type='value', data_type='', is_reference=False, is_qualifier=False, references=[],
                   qualifiers=[], rank='', prop_nr=prop_nr)


class WDString(WDBaseDataType):
    """
    Implements the Wikidata data type 'string'
    """
    DTYPE = 'string'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param value: The string to be used as the value
        :type value: str
        :param prop_nr: The WD item ID for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        super(WDString, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                       is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                       qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.set_value(value=value)

    def set_value(self, value):
        self.value = value

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

        super(WDString, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])


class WDItemID(WDBaseDataType):
    """
    Implements the Wikidata data type with a value being another WD item ID
    """
    DTYPE = 'wikibase-item'
    sparql_query = '''
        SELECT * WHERE {{
            ?item_id wdt:{0} wd:Q{1} .
        }}
    '''

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param value: The WD item ID to serve as the value
        :type value: str with a 'Q' prefix, followed by several digits or only the digits without the 'Q' prefix
        :param prop_nr: The WD item ID for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        super(WDItemID, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                       is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                       qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.set_value(value=value)

    def set_value(self, value):
        if value is None:
            self.value = None
        elif type(value) == int:
            self.value = value
        elif value[0] == 'Q':
            pattern = re.compile('[0-9]*')
            matches = pattern.match(value[1:])

            if len(value[1:]) == len(matches.group(0)):
                self.value = int(value[1:])
            else:
                raise ValueError('Invalid WD item ID, format must be "Q[0-9]*"')

        self.json_representation['datavalue'] = {
            'value': {
                'entity-type': 'item',
                'numeric-id': self.value
            },
            'type': 'wikibase-entityid'
        }

        super(WDItemID, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value']['numeric-id'], prop_nr=jsn['property'])


class WDProperty(WDBaseDataType):
    """
    Implements the Wikidata data type with value 'property'
    """
    DTYPE = 'wikibase-property'
    sparql_query = '''
        SELECT * WHERE {{
            ?item_id wdt:{0} wd:P{1} .
        }}
    '''

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param value: The WD property number to serve as a value
        :type value: str with a 'P' prefix, followed by several digits or only the digits without the 'P' prefix
        :param prop_nr: The WD property number for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        super(WDProperty, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                         is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                         qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.set_value(value=value)

    def set_value(self, value):
        # check if WD item or property ID is in valid format
        if value is None:
            self.value = None
        elif type(value) == int:
            self.value = value
        elif value[0] == 'P':
            pattern = re.compile('[0-9]*')
            matches = pattern.match(value[1:])

            if len(value[1:]) == len(matches.group(0)):
                self.value = int(value[1:])
            else:
                raise ValueError('Invalid WD property ID, format must be "P[0-9]*"')

        self.json_representation['datavalue'] = {
            'value': {
                'entity-type': 'property',
                'numeric-id': self.value
            },
            'type': 'wikibase-entityid'
        }

        super(WDProperty, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value']['numeric-id'], prop_nr=jsn['property'])


class WDTime(WDBaseDataType):
    """
    Implements the Wikidata data type with date and time values
    """
    DTYPE = 'time'

    def __init__(self, time, prop_nr, precision=11, timezone=0, calendarmodel='http://www.wikidata.org/entity/Q1985727',
                 is_reference=False, is_qualifier=False, snak_type='value', references=[], qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param time: A time representation string in the following format: '+%Y-%m-%dT%H:%M:%SZ'
        :type time: str in the format '+%Y-%m-%dT%H:%M:%SZ', e.g. '+2001-12-31T12:01:13Z'
        :param prop_nr: The WD property number for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param precision: Precision value for dates and time as specified in the WD data model (https://www.mediawiki.org/wiki/Wikibase/DataModel#Dates_and_times)
        :type precision: int
        :param timezone: The timezone which applies to the date and time as specified in the WD data model
        :type timezone: int
        :param calendarmodel: The calendar model used for the date. URL to the WD calendar model item.
        :type calendarmodel: str
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        # the value is composed of what is requried to define the WD time object
        value = (time, timezone, precision, calendarmodel)

        super(WDTime, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.set_value(value=value)

    def set_value(self, value):
        self.time, self.timezone, self.precision, self.calendarmodel = value
        self.json_representation['datavalue'] = {
            'value': {
                'time': self.time,
                'timezone': self.timezone,
                'before': 0,
                'after': 0,
                'precision': self.precision,
                'calendarmodel': self.calendarmodel
            },
            'type': 'time'
        }

        super(WDTime, self).set_value(value=self.time)

        if self.time is not None:
            if self.precision < 0 or self.precision > 14:
                raise ValueError('Invalid value for time precision, '
                                 'see https://www.mediawiki.org/wiki/Wikibase/DataModel/JSON#time')

            try:
                if self.time[6:8] != '00' and self.time[9:11] != '00':
                    datetime.datetime.strptime(self.time, '+%Y-%m-%dT%H:%M:%SZ')
            except ValueError as e:
                raise ValueError('Wrong data format, date format must be +%Y-%m-%dT%H:%M:%SZ')

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(time=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])

        value = jsn['datavalue']['value']
        return cls(time=value['time'], prop_nr=jsn['property'], precision=value['precision'],
                   timezone=value['timezone'], calendarmodel=value['calendarmodel'])


class WDUrl(WDBaseDataType):
    """
    Implements the Wikidata data type for URL strings
    """
    DTYPE = 'url'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param value: The URL to be used as the value
        :type value: str
        :param prop_nr: The WD item ID for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        super(WDUrl, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                                    is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.set_value(value)

    def set_value(self, value):
        if value is None:
            self.value = None
        else:
            protocols = ['http://', 'https://', 'ftp://', 'irc://']
            if True not in [True for x in protocols if value.startswith(x)]:
                raise ValueError('Invalid URL')

            self.value = value

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

        super(WDUrl, self).set_value(value=self.value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])

        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])


class WDMonolingualText(WDBaseDataType):
    """
    Implements the Wikidata data type for Monolingual Text strings
    """
    DTYPE = 'monolingualtext'

    def __init__(self, value, prop_nr, language='en', is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param value: The language specific string to be used as the value
        :type value: str
        :param prop_nr: The WD item ID for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param language: Specifies the WD language the value belongs to
        :type language: str
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        self.language = language
        value = (value, language)

        super(WDMonolingualText, self)\
            .__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                      is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.set_value(value)

    def set_value(self, value):

        self.json_representation['datavalue'] = {
            'value': {
                'text': value[0],
                'language': self.language
            },
            'type': 'monolingualtext'
        }

        super(WDMonolingualText, self).set_value(value=value[0])

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        value = jsn['datavalue']['value']
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])

        return cls(value=value['text'], prop_nr=jsn['property'], language=value['language'])


class WDQuantity(WDBaseDataType):
    """
    Implements the Wikidata data type for quantities
    """
    DTYPE = 'quantity'

    def __init__(self, value, prop_nr, upper_bound, lower_bound, unit='', is_reference=False, is_qualifier=False,
                 snak_type='value', references=[], qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param value: The quantity value
        :type value: float
        :param prop_nr: The WD item ID for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param upper_bound: Upper bound of the value if it exists, e.g. for standard deviations
        :type upper_bound: float
        :param lower_bound: Lower bound of the value if it exists, e.g. for standard deviations
        :type lower_bound: float
        :param unit: The WD unit item URL a certain quantity has been measured in (https://www.wikidata.org/wiki/Wikidata:Units)
        :type unit: str
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        value = (value, unit, upper_bound, lower_bound)

        super(WDQuantity, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.set_value(value)

    def set_value(self, value):
        value, unit, upper_bound, lower_bound = value

        if value is not None:
            # Integrity checks for value and bounds
            try:
                for i in [value, upper_bound, lower_bound]:
                    float(i)
            except ValueError as e:
                raise ValueError('Value, bounds and units must parse as integers or float')

            if float(lower_bound) > float(upper_bound) or float(lower_bound) > float(value):
                raise ValueError('Lower bound too large')

            if float(upper_bound) < float(value):
                raise ValueError('Upper bound too small')

        self.json_representation['datavalue'] = {
            'value': {
                'amount': str(value),
                'unit': str(unit),
                'upperBound': str(upper_bound),
                'lowerBound': str(lower_bound)
            },
            'type': 'quantity'
        }

        super(WDQuantity, self).set_value(value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        value = jsn['datavalue']['value']
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, upper_bound=None, lower_bound=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])

        return cls(value=value['amount'], prop_nr=jsn['property'], upper_bound=value['upperBound'],
                   lower_bound=value['lowerBound'], unit=value['unit'])


class WDCommonsMedia(WDBaseDataType):
    """
    Implements the Wikidata data type for Wikimedia commons media files
    """
    DTYPE = 'commonsMedia'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param value: The media file name from Wikimedia commons to be used as the value
        :type value: str
        :param prop_nr: The WD item ID for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        super(WDCommonsMedia, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                                             is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.set_value(value)

    def set_value(self, value):
        self.json_representation['datavalue'] = {
            'value': value,
            'type': 'string'
        }

        super(WDCommonsMedia, self).set_value(value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])


class WDGlobeCoordinate(WDBaseDataType):
    """
    Implements the Wikidata data type for globe coordinates
    """
    DTYPE = 'globe-coordinate'

    def __init__(self, latitude, longitude, precision, prop_nr, is_reference=False, is_qualifier=False,
                 snak_type='value', references=[], qualifiers=[], rank='normal'):
        """
        Constructor, calls the superclass WDBaseDataType
        :param latitude: Latitute in decimal format
        :type latitude: float
        :param longitude: Longitude in decimal format
        :type longitude: float
        :param precision: Precision of the position measurement
        :type precision: float
        :param prop_nr: The WD item ID for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A WD data type with subclass of WDBaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A WD data type with subclass of WDBaseDataType
        :param rank: WD rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """
        # TODO: implement globe parameter, so it becomes clear which globe the coordinates are referring to
        value = (latitude, longitude, precision)
        self.latitude, self.longitude, self.precision = value

        super(WDGlobeCoordinate, self)\
            .__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                      is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank,
                      prop_nr=prop_nr)

        self.set_value(value)

    def set_value(self, value):

        # TODO: Introduce validity checks for coordinates

        self.latitude, self.longitude, self.precision = value

        self.json_representation['datavalue'] = {
            'value': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'precision': self.precision,
                'globe': "http://www.wikidata.org/entity/Q2"
            },
            'type': 'globecoordinate'
        }

        super(WDGlobeCoordinate, self).set_value(self.latitude)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        value = jsn['datavalue']['value']
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(latitude=None, longitude=None, precision=None, prop_nr=jsn['property'],
                       snak_type=jsn['snaktype'])

        return cls(latitude=value['latitude'], longitude=value['longitude'], precision=value['precision'],
                   prop_nr=jsn['property'])


class WDApiError(Exception):
    def __init__(self, wd_error_message):
        """
        Base class for Wikidata error handling
        :param wd_error_message: The error message returned by the WD API
        :type wd_error_message: A Python json representation dictionary of the error message
        :return:
        """
        self.wd_error_msg = wd_error_message

    def __str__(self):
        return repr(self.wd_error_msg)


class NonUniqueLabelDescriptionPairError(WDApiError):
    def __init__(self, wd_error_message):
        """
        This class handles errors returned from the WD API due to an attempt to create an item which has the same
         label and description as an existing item in a certain language.
        :param wd_error_message: An WD API error mesage containing 'wikibase-validator-label-with-description-conflict'
         as the message name.
        :type wd_error_message: A Python json representation dictionary of the error message
        :return:
        """
        self.wd_error_msg = wd_error_message

    def get_language(self):
        """
        :return: Returns a 2 letter Wikidata language string, indicating the language which triggered the error
        """
        return self.wd_error_msg['error']['messages'][0]['parameters'][1]

    def get_conflicting_item_qid(self):
        """
        :return: Returns the QID string of the item which has the same label and description as the one which should
         be set.
        """
        qid_string = self.wd_error_msg['error']['messages'][0]['parameters'][2]

        return qid_string.split('|')[0][2:]


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


class MergeError(Exception):
    def __init__(self, value):
        self.value = value


    def __str__(self):
        return repr(self.value)
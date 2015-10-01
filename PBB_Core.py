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
import logging
import os

import PBB_Debug
import PBB_settings
# import mysql.connector
import socket
import getpass
import copy
import pprint
import wd_property_store
import json

'''
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
'''

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

    create_new_item = False
    log_file_name = ''

    def __init__(self, wd_item_id='', item_name='', domain='', data=[], server='www.wikidata.org',
                 append_value=[], references={}):
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
        self.domain = domain
        self.data = data
        self.server = server
        self.append_value = append_value
        self.references = references
        self.statements = []

        self.property_list = self.get_property_list()

        if self.item_name is not '' and self.domain is None and len(self.data) > 0:
            self.create_new_item = True
            return
        if self.item_name is '' and self.wd_item_id is '':
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

        if ('labels' not in self.wd_json_representation or 'en' not in self.wd_json_representation['labels']) and item_name != '':
            self.set_label(label=item_name, lang='en')

    def get_wd_entity(self):
        """
        retrieve a WD item in json representation from Wikidata
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

            wd_reply = reply.json()['entities'][self.wd_item_id]
            wd_reply = {x: wd_reply[x] for x in ('labels', 'descriptions', 'claims', 'aliases', 'sitelinks') if x in wd_reply}

            for prop in wd_reply['claims']:
                for z in wd_reply['claims'][prop]:
                    data_type = [x for x in WDBaseDataType.__subclasses__() if x.DTYPE == z['mainsnak']['datatype']][0]
                    # pprint.pprint(z)
                    statement = data_type.from_json(z)
                    self.statements.append(statement)

            return wd_reply

        except requests.HTTPError as e:
            self.log('ERROR', str(e))

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
        extract the properties which belong to the domain of the WD item
        :return: a dict with WD property strings as keys and empty strings as values
        """
        property_list = []
        for x in wd_property_store.wd_properties:
            if self.domain in wd_property_store.wd_properties[x]['domain']:
                property_list.append(x)

        return property_list

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
                        url = 'http://wdq.wmflabs.org/api'
                        params = {
                            'q': u'string[{}:{}]'.format(str(wd_property).replace('P', ''),
                                                         u'"{}"'.format(data_point)),
                        }

                        reply = requests.get(url, params=params)

                        tmp_qids = reply.json()['items']
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

        # sort the incoming data according to the WD property number
        self.data.sort(key=lambda z: z.get_prop_nr().lower())
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
                    if True not in [True if stat == x else False for x in prop_data]:
                        self.statements.insert(insert_pos + 1, stat)
                    continue

                # set all existing values of a property for removal
                for x in prop_data:
                    if x.get_id() != '':
                        setattr(x, 'remove', '')

                match = []
                for i in prop_data:
                    if stat == i:
                        match.append(True)
                        delattr(i, 'remove')
                        # TODO: Improve how to handle references. At minimum, the date should be updated if a
                        # value has been checked for validity.
                        if sum(map(lambda z: len(z), stat.get_references())) >= sum(map(lambda z: len(z), i.get_references())):
                            i.set_references(stat.get_references())
                        # current setting is to replace existing qualifiers
                        i.set_qualifiers(stat.get_qualifiers())
                    # if there is no value, do not add an element, this is also used to delete whole statements.
                    elif i.get_value() != '':
                        match.append(False)

                if True not in match:
                    self.statements.insert(insert_pos + 1, stat)

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
        selected but a ManualInterventionReqException() is raised.
        :return: boolean True if test passed
        """
        # generate a set containing all property number of the item currently loaded
        current_props_list = set([x.get_prop_nr() for x in self.statements])

        # compare the claim values of the currently loaded QIDs to the data provided in self.data
        count_existing_ids = 0
        for i in self.data:
            prop_nr = i.get_prop_nr()
            if prop_nr in wd_property_store.wd_properties:  # TODO: might want to restrict to self.domain only
                count_existing_ids += 1

        data_match_count = 0
        for new_stat in self.data:
            for stat in self.statements:
                if new_stat == stat:
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

        count = 0
        if len(current_props_list) - data_match_count > 0:
            count = round((len(current_props_list) - data_match_count) / 2)

        # Two thirds of the provided values must match, otherwise, raise exception
        majority_match = count_existing_ids - data_match_count > round(count_existing_ids * 0.66)

        # make decision if ManualInterventionReqException should be raised.
        if data_match_count < count and majority_match and self.item_name.lower() not in names:
            raise ManualInterventionReqException('Retrieved name does not match provided item name or core IDs. '
                                                 'Matching count {}, nonmatching count {}'
                                                 .format(data_match_count, count_existing_ids - data_match_count), '', '')
        else:
            return True

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

    def remove_sitelink(self, site):
        """
        Remove sitelinks to corresponding Wikipedia pages
        :param site: The Wikipedia page a sitelink is directed to (e.g. 'enwiki')
        :return:
        """
        if "sitelinks" in self.wd_json_representation.keys():
            if site in self.wd_json_representation['sitelinks']:
                returnvalue = self.wd_json_representation['sitelinks'][site]
                try:
                    del self.wd_json_representation['sitelinks'][site]
                except KeyError:
                    pass
                return returnvalue
        return None

    def get_sitelink(self, site):
        """
        A method to access the interwiki links in the json.model
        :return:
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
            u'data': json.JSONEncoder().encode(self.wd_json_representation),
            u'format': u'json',
            u'token': edit_token,
            u'bot': ''
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

            if 'error' in json_data.keys():
                PBB_Debug.prettyPrint(json_data)
                if 'wikibase-validator-label-with-description-conflict' == json_data['error']['messages'][0]['name']:
                    raise NonUniqueLabelDescriptionPairError(json_data)
                else:
                    raise WDApiError(json_data)

        except requests.HTTPError as e:
            repr(e)
            PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())

    @staticmethod
    def log(level, message):
        """
        A static method which initiates log files compatible to .csv format, allowing for easy further analysis.
        :param level: The log level as in the Python logging documentation, 5 different possible values with increasing
         severity
        :type level: String of value 'DEBUG', 'INFO', 'WARNING', 'ERROR' or 'CRITICAL'.
        :param message: The logging data which should be written to the log file. In order to achieve a csv-file
         compatible format, all fields must be separated by a colon. Furthermore, all strings which could contain colons,
         spaces or other special characters must be enclosed in double-quotes.
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
                    if 'hash' in qual:
                        qual_hash = qual['hash']

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
                mainsnak.set_rank = json_representation['rank']
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
        :type prop_nr: A string with a prefixed 'P' and several numbers e.g. 'P715' (Drugbank ID)
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
        self.prop_nr = prop_nr

        # WD internal ID and hash are issued by the WD servers
        self.id = ''
        self.hash = ''

        self.json_representation = {
            "snaktype": self.snak_type,
            "property": self.prop_nr,
            "datavalue": {},
            "datatype": self.data_type
        }

        snak_types = ['value', 'novalue', 'somevalue']
        if snak_type not in snak_types:
            raise ValueError('{} is not a valid snak type'.format(snak_type))

        if self.is_qualifier and self.is_reference:
            raise ValueError('A claim cannot be a reference and a qualifer at the same time')
        if (len(references) > 0 or len(self.qualifiers) > 0) and (self.is_qualifier or self.is_reference):
            raise ValueError('Qualifiers or references cannot have references')

    def __eq__(self, other):
        if self.get_value() == other.get_value() and self.get_prop_nr() == other.get_prop_nr():
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
        self.value = value

    def get_references(self):
        return self.references

    def set_references(self, references):
        if len(references) > 0 and (self.is_qualifier or self.is_reference):
            raise ValueError('Qualifiers or references cannot have references')

        self.references = references

    def get_qualifiers(self):
        return self.qualifiers

    def set_qualifiers(self, qualifiers):
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

    def set_id(self, id):
        self.id = id

    def set_hash(self, hash):
        self.hash = hash

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
    DTYPE = 'string'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):

        super(WDString, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])


class WDItemID(WDBaseDataType):
    DTYPE = 'wikibase-item'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal', entity_type='item'):

        # check if WD item or property ID is in valid format
        if type(value) == int:
            self.value = value
        elif value[0] == 'Q' or value[0] == 'P':
            pattern = re.compile('[0-9]*')
            matches = pattern.match(value[1:])

            if len(value[1:]) == len(matches.group(0)):
                self.value = int(value[1:])
            else:
                raise ValueError('Invalid WD item ID, format must be "Q[0-9]*"')

        # check for valid entity type
        entity_types = ['item', 'property']
        if entity_type not in entity_types:
            raise ValueError('Invalid entity type, "item" or "property" are allowed')

        super().__init__(value=self.value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.json_representation['datavalue'] = {
            'value': {
                'entity-type': 'item',
                'numeric-id': self.value
            },
            'type': 'wikibase-entityid'
        }

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        return cls(value=jsn['datavalue']['value']['numeric-id'], prop_nr=jsn['property'])


class WDTime(WDBaseDataType):
    DTYPE = 'time'

    def __init__(self, time, prop_nr, precision=11, timezone=0, calendarmodel='http://www.wikidata.org/entity/Q1985727',
                 is_reference=False, is_qualifier=False, snak_type='value', references=[], qualifiers=[], rank='normal'):
        """
        Constructor
        :param time: A time representation string in the following format: '+%Y-%m-%dT%H:%M:%SZ'
        :type time: str in the format '+%Y-%m-%dT%H:%M:%SZ', e.g. '+2001-12-31T12:01:13Z'
        :param prop_nr:
        :param precision:
        :param timezone:
        :param calendarmodel:
        :param is_reference:
        :param is_qualifier:
        :param snak_type:
        :param references:
        :param qualifiers:
        :param rank:
        :return:
        """
        if precision < 0 or precision > 14:
            raise ValueError('Invalid value for time precision, '
                             'see https://www.mediawiki.org/wiki/Wikibase/DataModel/JSON#time')

        try:
            datetime.datetime.strptime(time, '+%Y-%m-%dT%H:%M:%SZ')
        except ValueError as e:
            raise ValueError('Wrong data format, date format must be +%Y-%m-%dT%H:%M:%SZ')

        # the value is composed of what is requried to define the WD time object
        value = (time, timezone, precision, calendarmodel)

        super().__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.json_representation['datavalue'] = {
            'value': {
                'time': time,
                'timezone': timezone,
                'before': 0,
                'after': 0,
                'precision': precision,
                'calendarmodel': calendarmodel
            },
            'type': 'time'
        }

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        value = jsn['datavalue']['value']

        return cls(time=value['time'], prop_nr=jsn['property'], precision=value['precision'],
                   timezone=value['timezone'], calendarmodel=value['calendarmodel'])


class WDUrl(WDBaseDataType):
    DTYPE = 'url'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):

        protocols = ['http://', 'https://', 'ftp://', 'irc://']
        if True not in [True for x in protocols if value.startswith(x)]:
            raise ValueError('Invalid URL')

        super().__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])


class WDMonolingualText(WDBaseDataType):
    DTYPE = 'monolingualtext'

    def __init__(self, value, prop_nr, language='en', is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):

        value = (value, language)

        super().__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.json_representation['datavalue'] = {
            'value': {
                'text': value[0],
                'language': language
            },
            'type': 'monolingualtext'
        }

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        value = jsn['datavalue']['value']
        return cls(value=value['text'], prop_nr=jsn['property'], language=value['language'])


class WDQuantity(WDBaseDataType):
    DTYPE = 'quantity'

    def __init__(self, value, prop_nr, upper_bound, lower_bound, unit='1', is_reference=False, is_qualifier=False,
                 snak_type='value', references=[], qualifiers=[], rank='normal'):

        # Integrity checks for value and bounds
        try:
            for i in [value, upper_bound, lower_bound, unit]:
                int(i)
        except ValueError as e:
            raise ValueError('Value, bounds and units must be integers')

        if int(lower_bound) > int(upper_bound) or int(lower_bound) > int(value):
            raise ValueError('Lower bound too large')

        if int(upper_bound) < int(value):
            raise ValueError('Upper bound too small')

        value = (str(value), str(unit), str(upper_bound), str(lower_bound))

        super().__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.json_representation['datavalue'] = {
            'value': {
                'amount': str(value[0]),
                'unit': str(unit),
                'upperBound': str(upper_bound),
                'lowerBound': str(lower_bound)
            },
            'type': 'quantity'
        }

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        value = jsn['datavalue']['value']

        return cls(value=value['amount'], prop_nr=jsn['property'], upper_bound=value['upperBound'],
                   lower_bound=value['lowerBound'], unit=value['unit'])


class WDCommonsMedia(WDBaseDataType):
    DTYPE = 'commonsMedia'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=[],
                 qualifiers=[], rank='normal'):

        super().__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])

class WDGlobeCoordinate(WDBaseDataType):
    DTYPE = 'globe-coordinate'

    def __init__(self, latitude, longitude, precision, prop_nr, is_reference=False, is_qualifier=False,
                 snak_type='value', references=[], qualifiers=[], rank='normal'):

        # TODO: Introduce validity checks for coordinates

        value = (latitude, longitude, precision)

        super().__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                         is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr)

        self.latitude = latitude
        self.longitude = longitude
        self.precision = precision
        self.json_representation['datavalue'] = {
            'value': {
                'latitude': latitude,
                'longitude': longitude,
                'precision': precision,
                'globe': "http://www.wikidata.org/entity/Q2"
            },
            'type': 'globecoordinate'
        }

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        value = jsn['datavalue']['value']
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


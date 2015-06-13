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
import urllib2



import PBB_Debug
import PBB_Functions
import PBB_settings
import mysql.connector
import socket
import getpass

import wd_property_store
try:
    import simplejson as json
except:
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
        
        
        

class WDItem(object):
    def __init__(self, wdItemID):
        self.id = wdItemID
        self.wdContent = self.getItems(wdItemID)
        self.properties = self.getProperties()
        
    def getItems(self, wdItem):
        query = 'https://www.wikidata.org/w/api.php?action=wbgetentities{}{}{}'.format(
            '&ids='+wdItem,
            '&props=labels|aliases|claims',
            '&format=json'
        )
        return(json.load(urllib2.urlopen(query)))
        
    def getProperties(self):
        return self.wdContent["entities"][self.id]["claims"].keys()

class WDItemList(object):
    def __init__(self, wdproperty):
        self.wdproperty = wdproperty
        self.wditems = getItemsByProperty(self, wdproperty)

    def getItemsByProperty(self, wdproperty):
        """
        Gets all WikiData item IDs that contains statements containing property wdproperty
        """
        req = urllib2.Request("http://wdq.wmflabs.org/api?q=claim%5B"+wdproperty+"%5D&props="+wdproperty, None, {'user-agent':'proteinBoxBot'})
        opener = urllib2.build_opener()
        f = opener.open(req)
        return json.load(f)

class WDItemEngine(object):

    wd_item_id = ''
    item_names = ''
    domain = ''
    autoadd_references = False
    normalize = True
    create_new_item = False
    data = {}

    # a list with all properties an item should have and/or modify
    property_list = {}
    wd_json_representation = ''

    def __init__(self, wd_item_id='', item_name='', normalize=True, domain='', data={}):
        """
        constructor
        :param wd_item_id: Wikidata item id
        :param item_name: Label of the wikidata item
        :param normalize: boolean if wbgetentity should use the parameter normalize
        :param domain: string which tells the data domain the class should operate in
        :param data: a dictionary with WD property strings as keys and the data which should be written to
        a WD item as the property values
        """
        self.wd_item_id = wd_item_id
        self.item_names = item_name
        self.domain = domain
        self.autoadd_references = False
        self.normalize = normalize
        self.data = data

        self.get_item_data(item_name, wd_item_id)
        self.property_list = self.get_property_list()

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
                qids_by_string = self.get_wd_search_results(item_name)
                qids_by_props = self.__select_wd_item()
                if qids_by_props is not '':
                    self.wd_item_id = qids_by_props

            except WDSearchError as e:
                PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
                print(e)

    def get_wd_entity(self, item=''):
        """
        retrieve a WD item in json representation from Wikidata
        :param item: string which represents the wikidata QID
        :return: python complex dictionary represenation of a json
        """
        try:
            query = 'https://www.wikidata.org/w/api.php?action=wbgetentities{}{}{}{}{}'.format(
                '&sites=enwiki',
                '&languages=en',
                '&ids=' + urllib2.quote(item),
                '&props=labels|aliases|claims',
                '&format=json'
            )

            return(json.load(urllib2.urlopen(query)))

        except urllib2.HTTPError as e:
            PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
            print(e)

    def get_wd_search_results(self, search_string=''):
        """
        Performs a search in WD for a certain WD search string
        :param search_string: a string which should be searched for in WD
        :return: returns a list of QIDs found in the search
        """
        try:
            query = 'https://www.wikidata.org/w/api.php?action=wbsearchentities{}{}'.format(
                '&language=en',
                '&search=' + urllib2.quote(search_string)
            )

            search_results = json.load(urllib2.urlopen(query))

            if search_results['success'] != 1:
                raise WDSearchError('WD search failed')
            elif len(search_results['search']) > 0:
                return([])
            else:
                id_list = []
                for i in search_results['search']:
                    id_list.append(i['id'])

                return(id_list)

        except urllib2.HTTPError as e:
            PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
            print(e)

    def get_property_list(self):
        """
        extract the properties which belong to the domain of the WD item
        :return: a dict with WD property strings as keys and empty strings as values
        """
        property_list = []
        for x in wd_property_store.wd_properties:
            if self.domain in wd_property_store.wd_properties[x]['domain']:
                property_list['x'] = ''

        return(property_list)

    def __select_wd_item(self, item_list):
        """
        The most likely WD item QID should be returned, after querying WDQ for all core_id properties
        :param item_list: a list of QIDs returned by a string search in WD
        :return:
        """
        qid_list = []
        for wd_property in self.data:
            try:
                # check if the property is a core_id and should be unique for every WD item
                if wd_property_store[wd_property]['core_id'] == 'True':
                    query = urllib2.quote('http://wdq.wmflabs.org/api?q=string[{}:{}]'.format(wd_property, self.data[wd_property]))
                    tmp_qids = json.load(urllib2.urlopen(query))['status']['items']
                    qid_list.append(tmp_qids)

                    if len(tmp_qids) > 1:
                        raise ManualInterventionReqException('More than one WD item has the same property value', wd_property, tmp_qids)

            except urllib2.HTTPError as e:
                PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
                print(e)

        if len(qid_list) == 0:
            self.create_new_item = True
            return('')

        unique_qids = set(qid_list)
        if len(unique_qids) > 1:
            # FIX: exception should be given a list at param 2 which properties are causing the conflicts
            raise ManualInterventionReqException('More than one WD item has the same property value', 'implementation req', unique_qids)
        elif len(unique_qids) == 1:
            return(list(unique_qids)[0])

    def getItemsByProperty(self, wdproperty):
        """
        Gets all WikiData item IDs that contains statements containing property wdproperty
        """
        query - 'http'
        req = urllib2.Request("http://wdq.wmflabs.org/api?q=claim%5B"+wdproperty+"%5D&props="+wdproperty, None, {'user-agent':'proteinBoxBot'})
        opener = urllib2.build_opener()
        f = opener.open(req)
        return(json.load(f))
        
    def getClaims(self, wdItem, claimProperty):
        """
        Returns all property values in a given wdItem
        """
        query = 'https://www.wikidata.org/w/api.php?action=wbgetclaims{}{}{}'.format(
            '&entity='+wdItem.getID() ,
            'property'+claimProperty
        )        
        params = {
                    'entity': wdItem.getID(),
                    'property': claimProperty,
                 }
        return(json.load(urllib2.urlopen(query)))

    def countPropertyValues(self, wdItem, claimProperty):
        '''
        Count the number of claims with a given property
        '''
        data = getClaims(wdItem, claimProperty)
        return len(data["claims"][claimProperty])

    def add_property(self, property):
        """
        :param property: takes a property the WDItem should have
        :return: None
        """
        pass

    def add_reference(self, wd_property, reference_type, reference_item):
        """
        Call this method to add a reference to a statement/claim
        :param wd_property: the Wikidata property number a reference should be added to
        :param reference_type: The reference property number (e.g. stated in (P248), imported from (P143))
        :param reference_item: the item a reference should point to
        :return: None
        """
        found = False
        for ref in references:
          if property in ref["snaks"]:
            for snak in ref["snaks"][property]:
              if snak["datavalue"]["value"]["numeric-id"] == itemId:
                ref = setDateRetrievedTimestamp(ref)
                found = True
                break
        if not found:    
            reference = dict()
            snaks = dict()
            reference["snaks"] = snaks
            snaks[property]=[]
            reference['snaks-order']=['P143']
            snak=dict()
            snaks[property].append(snak)
            snak['property']=property
            snak["snaktype"]='value'
            snak["datatype"]='wikibase-item'
            snak["datavalue"]=dict()
            snak["datavalue"]["type"]='wikibase-entityid'
            snak["datavalue"]["value"]=dict()
            snak["datavalue"]["value"]["entity-type"]='item'
            snak["datavalue"]["value"]["numeric-id"]=itemId
            reference = setDateRetrievedTimestamp(reference)
            if stated:
                reference = setStatedIn(reference)
            references.append(reference)
        
    def setDateRetrievedTimestamp(self, reference):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('+0000000%Y-%m-%dT00:00:00Z')
        wdTimestamp = dict()
        reference["snaks-order"]=['P143', 'P813']                 
        wdTimestamp["datatype"]='time'
        wdTimestamp["property"]='P813'
        wdTimestamp["snaktype"]='value'
        wdTimestamp["datavalue"]=dict()
        wdTimestamp["datavalue"]["type"]='time'
        wdTimestamp["datavalue"]["value"]=dict()
        wdTimestamp["datavalue"]["value"]["after"]=0
        wdTimestamp["datavalue"]["value"]["before"]=0
        wdTimestamp["datavalue"]["value"]["calendarmodel"]='http://www.wikidata.org/entity/Q1985727'
        wdTimestamp["datavalue"]["value"]["precision"]=11
        wdTimestamp["datavalue"]["value"]["time"]=timestamp
        wdTimestamp["datavalue"]["value"]["timezone"]=0
        reference["snaks"]['P813']=[wdTimestamp]
        return reference

    def setStatedIn(self, reference):
        doDate =  globalDiseaseOntology.findall('.//oboInOwl:date', namespaces)
        dateList = doDate[0].text.split(' ')[0].split(":")
        searchTerm = "Disease ontology release "+dateList[2]+"-"+dateList[1]+"-"+dateList[0]
        snak = dict()      
        snak["datatype"]='wikibase-item'
        snak["property"]='P248'
        snak["snaktype"]='value'
        snak["datavalue"]=dict()
        snak["datavalue"]["type"]='wikibase-entityid'
        snak["datavalue"]["value"]=dict()
        snak["datavalue"]["value"]["entity-type"]='item'
        searchResult = getItems(globalSite, searchTerm)['search'][0]["id"]
        snak["datavalue"]["value"]["numeric-id"]=int(searchResult[1:])
        print "gglobalWikidataID: "+globalWikidataID
        print "searchResult: "+searchResult
        if globalWikidataID != searchResult:
            reference["snaks-order"]=['P143', 'P248', 'P813']
            reference["snaks"]['P248']=[snak]
        return reference

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

    def write(self):
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


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
import time
import datetime
import json
import urllib2
import PBB_Debug

class WDItemEngine(object):

    wd_item_id = ''
    item_names = ''
    autoadd_references = False

    # a list with all properties an item should have and/or modify
    property_list = []
    wd_json_representation = ''

    def __init__(self, wd_item_id='', item_names=[]):
        """
        constructor
        :param wd_item_id: Wikidata item id
        :param item_names: Label of the wikidata item
        """
        self.wd_item_id = wd_item_id
        self.item_names = item_names
        self.autoadd_references = False

        self.wd_json_representation = self.get_item_data(item_names[0], wd_item_id)

    def get_item_data(self, item_name=None, item_id=None, normalize=True):
        """
        Instantiate a class by either providing a item name or a Wikidata item ID
        :param item_name: A name which should allow to find an item in Wikidata
        :param item_id: Wikidata item ID which allows loading of a Wikidata item
        :param normalize: Set to true if the WD api call should use the normalize parameter
        :return: None
        """
        if item_name is None and item_id is None:
            raise IDMissingError('No item name or WD identifyer was given')

        try:
            title_string = ''
            if item_id is not None:
                title_string = '&ids={}'.format(item_id)
            elif item_name is not None:
                title_string = '&titles={}'.format(urllib2.quote(item_name))

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
            PBB_Debug.getSentryClient().captureException(PBB_Debug.getSentryClient())
            print(e)
         
    def getItemsByProperty(wdproperty):
        """
        Gets all WikiData item IDs that contains statements containing property wdproperty
        """
        query - 'http'
        req = urllib2.Request("http://wdq.wmflabs.org/api?q=claim%5B"+wdproperty+"%5D&props="+wdproperty, None, {'user-agent':'proteinBoxBot'})
        opener = urllib2.build_opener()
        f = opener.open(req)
        return simplejson.load(f)
        
    def getClaims(wdItem, claimProperty):
        """
        Returns all property values in a given wdItem
        """
        query = 'https://www.wikidata.org/w/api.php?action=wbgetclaims{}{}{}'.format(
            '&entity='+wdItem.getID() ,
            'property'=claimProperty
        )        
        params = {
                    'entity' : wdItem.getID(),
        			'property': claimProperty,
                 }
        return(json.load(urllib2.urlopen(query)))
        
    
    def countPropertyValues(wdItem, claimProperty):
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

    def add_reference(self, property, reference_type, reference_item):
        """
        Call this method to add a reference to a statement/claim
        :param property: the Wikidata property number a reference should be added to
        :param reference_type: The reference property number (e.g. stated in (P248), imported from (P143))
        :param reference_item: the item a reference should point to
        :return: None
        """
        found = False
        for ref in references:
          if property in ref["snaks"]:
            for snak in ref["snaks"][property]:
              if snak["datavalue"]["value"]["numeric-id"]==itemId:
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


import copy
import datetime
import json
import logging
import os
import re
import time
import warnings
from collections import defaultdict
from typing import List

import pandas as pd
import requests
from pyshex import ShExEvaluator
from rdflib import Graph
from shexer.shaper import Shaper

from wikidataintegrator.wdi_backoff import wdi_backoff
from wikidataintegrator.wdi_config import config
from wikidataintegrator.wdi_fastrun import FastRunContainer
from wikidataintegrator.wdi_helpers import MappingRelationHelper
from wikidataintegrator import wdi_rdf

"""
Authors:
Andra Waagmeester (andra' at ' micelio.be)
Gregory Stupp (stuppie' at 'gmail.com )
Sebastian Burgstaller (sebastian.burgstaller' at 'gmail.com

This file is part of the WikidataIntegrator.

"""

__author__ = 'Andra Waagmeester, Gregory Stupp, Sebastian Burgstaller '
__license__ = 'MIT'

class WDFunctionsEngine(object):
    def __init__(self, mediawiki_api_url=None, sparql_endpoint_url=None,):
        self.mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url
        self.sparql_endpoint_url = config['SPARQL_ENDPOINT_URL'] if sparql_endpoint_url is None else sparql_endpoint_url

    @staticmethod
    def get_rdf(wd_item_id='', format="turtle", mediawiki_api_url=None):

        """
        function to get RDF of a Wikidata item

        :param wd_item_id='': Wikidata identifier to extract the RDF of
        :param format RDF from to return takes (turtle, ntriples, rdfxml,)
        :param mediawiki_api_url: default to wikidata's api, but can be changed to any wikibase

        :return:
        """
        localcopy = Graph()
        localcopy.parse(config["CONCEPT_BASE_URI"] + wd_item_id + ".ttl")
        return localcopy.serialize(format=format)

    @staticmethod
    def get_linked_by(qid, mediawiki_api_url=None):
        """
            :param qid: Wikidata identifier to which other wikidata items link
            :param mediawiki_api_url: default to wikidata's api, but can be changed to any wikibase
            :return:
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url

        linkedby = []
        whatlinkshere = json.loads(requests.get(
            mediawiki_api_url + "?action=query&list=backlinks&format=json&bllimit=500&bltitle=" + qid).text)
        for link in whatlinkshere["query"]["backlinks"]:
            if link["title"].startswith("Q"):
                linkedby.append(link["title"])
        while 'continue' in whatlinkshere.keys():
            whatlinkshere = json.loads(requests.get(
                mediawiki_api_url + "?action=query&list=backlinks&blcontinue=" +
                whatlinkshere['continue']['blcontinue'] + "&format=json&bllimit=500&bltitle=" + qid).text)
            for link in whatlinkshere["query"]["backlinks"]:
                if link["title"].startswith("Q"):
                    linkedby.append(link["title"])
        return linkedby

    @staticmethod
    @wdi_backoff()
    def execute_sparql_query(query, prefix=None, endpoint=None, user_agent=None, as_dataframe=False, max_retries=1000, retry_after=60):

        """
        Static method which can be used to execute any SPARQL query

        :param prefix: The URI prefixes required for an endpoint, default is the Wikidata specific prefixes
        :param query: The actual SPARQL query string
        :param endpoint: The URL string for the SPARQL endpoint. Default is the URL for the Wikidata SPARQL endpoint
        :param user_agent: Set a user agent string for the HTTP header to let the WDQS know who you are.
        :param as_dataframe: Return result as pandas dataframe
        :type user_agent: str
        :param max_retries: The number time this function should retry in case of header reports.
        :param retry_after: the number of seconds should wait upon receiving either an error code or the WDQS is not reachable.
        :return: The results of the query are returned in JSON format
        """

        sparql_endpoint_url = config['SPARQL_ENDPOINT_URL'] if endpoint is None else endpoint
        user_agent = config['USER_AGENT_DEFAULT'] if user_agent is None else user_agent

        if prefix:
            query = prefix + '\n' + query

        params = {
            'query': '#Tool: wdi_core fastrun\n' + query,
            'format': 'json'
        }

        headers = {
            'Accept': 'application/sparql-results+json',
            'User-Agent': user_agent
        }
        response = None

        for n in range(max_retries):
            try:
                response = requests.post(sparql_endpoint_url, params=params, headers=headers)
            except requests.exceptions.ConnectionError as e:
                print("Connection error: {}. Sleeping for {} seconds.".format(e, retry_after))
                time.sleep(retry_after)
                continue
            if response.status_code == 503:
                print("service unavailable. sleeping for {} seconds".format(retry_after))
                time.sleep(retry_after)
                continue
            if response.status_code == 429:
                if "retry-after" in response.headers.keys():
                    retry_after = response.headers["retry-after"]
                print("service unavailable. sleeping for {} seconds".format(retry_after))
                time.sleep(retry_after)
                continue
            response.raise_for_status()
            results = response.json()

            if as_dataframe:
                return WDItemEngine._sparql_query_result_to_df(results)
            else:
                return results

    @staticmethod
    def _sparql_query_result_to_df(results):

        def parse_value(item):
            if item.get("datatype") == "http://www.w3.org/2001/XMLSchema#decimal":
                return float(item['value'])
            if item.get("datatype") == "http://www.w3.org/2001/XMLSchema#integer":
                return int(item['value'])
            if item.get("datatype") == "http://www.w3.org/2001/XMLSchema#dateTime":
                return datetime.datetime.strptime(item['value'], '%Y-%m-%dT%H:%M:%SZ')
            return item['value']

        results = results['results']['bindings']
        results = [{k: parse_value(v) for k, v in item.items()} for item in results]
        df = pd.DataFrame(results)
        return df

    @staticmethod
    def delete_item(item, reason, login, mediawiki_api_url=None, user_agent=None):
        """
        Takes a list of items and posts them for deletion by Wikidata moderators, appends at the end of the deletion
        request page.

        :param item: a QID which should be deleted
        :type item: string
        :param reason: short text about the reason for the deletion request
        :type reason: str
        :param login: A WDI login object which contains username and password the edit should be performed with.
        :type login: wdi_login.WDLogin
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url
        user_agent = config['USER_AGENT_DEFAULT'] if user_agent is None else user_agent

        params = {
            'action': 'delete',
            'title': 'Item:' + item,
            'reason': reason,
            'token': login.get_edit_token(),
            'format': 'json'
        }
        headers = {
            'User-Agent': user_agent
        }
        r = requests.post(url=mediawiki_api_url, data=params, cookies=login.get_edit_cookie(), headers=headers)
        print(r.json())

    @staticmethod
    def delete_statement(statement_id, revision, login, mediawiki_api_url='https://www.wikidata.org/w/api.php',
                         user_agent=config['USER_AGENT_DEFAULT']):
        params = {
            'action': 'wbremoveclaims',
            'claim': statement_id,
            'token': login.get_edit_token(),
            'baserevid': revision,
            'bot': True,
            'format': 'json'
        }
        headers = {
            'User-Agent': user_agent
        }
        r = requests.post(url=mediawiki_api_url, data=params, cookies=login.get_edit_cookie(), headers=headers)
        print(r.json())

    ## SHEX related functions
    @staticmethod
    def check_shex_conformance(qid=None,data=None, eid=None, entity_schema_repo=None, output='confirm'):
        """
                Static method which can be used to check for conformance of a Wikidata item to an EntitySchema any SPARQL query

                :param qid: The URI prefixes required for an endpoint, default is the Wikidata specific prefixes
                :param eid: The EntitySchema identifier from Wikidata
                :param sparql_endpoint_url: The URL string for the SPARQL endpoint. Default is the URL for the Wikidata SPARQL endpoint
                :param output: results of a test of conformance on a given shape expression
                :return: The results of the query are returned in string format
        """
        if not bool(qid):
            raise ValueError('Please provide  a QID even with a json object of a Wikidata item')

        rdfdata = Graph()
        if not bool(data):
            rdfdata.parse(config["CONCEPT_BASE_URI"] + qid + ".ttl")
        else:
            rdfdata.parse(data=data)
        entity_schema_repo = config["ENTITY_SCHEMA_REPO"] if entity_schema_repo is None else entity_schema_repo
        schema = requests.get(entity_schema_repo+eid).text

        for result in ShExEvaluator(rdf=rdfdata, schema=schema, focus=config["CONCEPT_BASE_URI"] + qid).evaluate():
            shex_result = dict()
            if result.result:
                shex_result["result"] = True
            else:
                shex_result["result"] = False
            shex_result["reason"] = result.reason
            shex_result["focus"] = result.focus

        if output == "confirm":
            return shex_result["result"]
        elif output == "reason":
            return shex_result["reason"]
        else:
            return shex_result

    @staticmethod
    def extract_shex(qid, extract_shape_of_qualifiers=False, just_direct_properties=True,
                     comments=False, endpoint="https://query.wikidata.org/sparql"):
        """
        It extracts a shape tor the entity specified in qid. The shape is built w.r.t the outgoing
        properties of the selected Wikidata entity.
        Optionally, it generates as well a shape for each qualifier.

        :param qid: Wikidata identifier to which other wikidata items link
        :param extract_shape_of_qualifiers: It it is set to True, the result will contain the shape of the qid
                selected but also the shapes of its qualifiers.
        :param just_direct_properties: If it set to True, the shape obtained will just contain direct properties to other
                Wikidata items. It will ignore qualifiers. Do not set to True if extract_shape_of_qualifiers is True
        :param comments: If it is set to True, each triple constraint will have an associated comment that indicates
               the trustworthiness of each triple constraint. This is usefull for shapes that have been extracted
               w.r.t to the properties of more than one entity.
        :param endpoint: The URL string for the SPARQL endpoint. Default is the URL for the Wikidata SPARQL endpoint
        :return: shex content in String format
        """
        namespaces_dict = {
            "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
            "http://www.wikidata.org/prop/": "p",
            "http://www.wikidata.org/prop/direct/": "wdt",
            "http://www.wikidata.org/entity/": "wd",
            "http://www.w3.org/2001/XMLSchema#": "xsd",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
            "http://www.w3.org/XML/1998/namespace": "xml",
            "http://wikiba.se/ontology#": "wikibase",
            "http://schema.org/": "schema",
            "http://www.w3.org/2004/02/skos/core#": "skos"
        }
        namespaces_to_ignore = [  # Ignoring these namespaces, mainly just direct properties are considered.
            "http://www.wikidata.org/prop/",
            "http://www.wikidata.org/prop/direct-normalized/",
            "http://schema.org/",
            "http://www.w3.org/2004/02/skos/core#",
            "http://wikiba.se/ontology#",
            "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "http://www.w3.org/2000/01/rdf-schema#"
        ]

        shape_map = "<http://www.wikidata.org/entity/{qid}>@<{qid}>".format(qid=qid)
        shaper = Shaper(shape_map_raw=shape_map,
                        url_endpoint=endpoint,
                        disable_comments=not comments,
                        shape_qualifiers_mode=extract_shape_of_qualifiers,
                        namespaces_dict=namespaces_dict,
                        namespaces_to_ignore=namespaces_to_ignore if just_direct_properties else None,
                        namespaces_for_qualifier_props=["http://www.wikidata.org/prop/"],
                        depth_for_building_subgraph=2 if extract_shape_of_qualifiers else 1)
        return shaper.shex_graph(string_output=True,
                                 acceptance_threshold=0)


class WDItemEngine(object):
    databases = {}
    pmids = []

    log_file_name = ''
    fast_run_store = []

    DISTINCT_VALUE_PROPS = dict()

    logger = None

    def __init__(self, wd_item_id='', new_item=False, data=None, mediawiki_api_url=None, sparql_endpoint_url=None,
                 wikibase_url=None, concept_base_uri=None, append_value=None, fast_run=False, fast_run_base_filter=None,
                 fast_run_use_refs=False, ref_handler=None, global_ref_mode='KEEP_GOOD', good_refs=None,
                 keep_good_ref_statements=False, search_only=False, item_data=None, user_agent=None, core_props=None,
                 core_prop_match_thresh=0.66, property_constraint_pid=None, distinct_values_constraint_qid=None,
                 fast_run_case_insensitive=False, debug=False):
        """
        constructor

        :param wd_item_id: Wikidata item id
        :param new_item: This parameter lets the user indicate if a new item should be created
        :type new_item: True or False
        :param data: a dictionary with WD property strings as keys and the data which should be written to
        a WD item as the property values
        :type data: List[WDBaseDataType]
        :param append_value: a list of properties where potential existing values should not be overwritten by the data
        passed in the :parameter data.
        :type append_value: list of property number strings
        :param fast_run: True if this item should be run in fastrun mode, otherwise False. User setting this to True
        should also specify the fast_run_base_filter for these item types
        :type fast_run: bool
        :param fast_run_base_filter: A property value dict determining the Wikidata property and the corresponding value
        which should be used as a filter for this item type. Several filter criteria can be specified. The values
        can be either Wikidata item QIDs, strings or empty strings if the value should be a variable in SPARQL.
        Example: {'P352': '', 'P703': 'Q15978631'} if the basic common type of things this bot runs on is
        human proteins (specified by Uniprot IDs (P352) and 'found in taxon' homo sapiens 'Q15978631').
        :type fast_run_base_filter: dict
        :param fast_run_use_refs: If `True`, fastrun mode will consider references in determining if a statement should
        be updated and written to Wikidata. Otherwise, only the value and qualifiers are used. Default: False
        :type fast_run_use_refs: bool
        :param ref_handler: This parameter defines a function that will manage the reference handling in a custom
        manner. This argument should be a function handle that accepts two arguments, the old/current statement
        (first argument) and new/proposed/to be written statement (second argument), both of type: a subclass of
        WDBaseDataType. The function should return an new item that is the item to be written. The item's values
        properties or qualifiers should not be modified; only references. This function is also used in fastrun mode.
        This will only be used if the ref_mode is set to "CUSTOM".
        :type ref_handler: function
        :param global_ref_mode: sets the reference handling mode for an item. Four modes are possible, 'STRICT_KEEP'
        keeps all references as they are, 'STRICT_KEEP_APPEND' keeps the references as they are and appends
        new ones. 'STRICT_OVERWRITE' overwrites all existing references for given. 'CUSTOM' will use the function
        defined in ref_handler
        :type global_ref_mode: str of value 'STRICT_KEEP', 'STRICT_KEEP_APPEND', 'STRICT_OVERWRITE', 'KEEP_GOOD', 'CUSTOM'
        :param good_refs: This parameter lets the user define blocks of good references. It is a list of dictionaries.
        One block is a dictionary with  Wikidata properties as keys and potential values as the required value for
        a property. There can be arbitrarily many key: value pairs in one reference block.
        Example: [{'P248': 'Q905695', 'P352': None, 'P407': None, 'P1476': None, 'P813': None}]
        This example contains one good reference block, stated in: Uniprot, Uniprot ID, title of Uniprot entry,
        language of work and date when the information has been retrieved. A None type indicates that the value
        varies from reference to reference. In this case, only the value for the Wikidata item for the
        Uniprot database stays stable over all of these references. Key value pairs work here, as Wikidata
        references can hold only one value for one property. The number of good reference blocks is not limited.
        This parameter OVERRIDES any other reference mode set!!
        :type good_refs: list containing dictionaries.
        :param keep_good_ref_statements: Do not delete any statement which has a good reference, either defined in the
        good_refs list or by any other referencing mode.
        :type keep_good_ref_statements: bool
        :param search_only: If this flag is set to True, the data provided will only be used to search for the
        corresponding Wikidata item, but no actual data updates will performed. This is useful, if certain states or
        values on the target item need to be checked before certain data is written to it. In order to write new
        data to the item, the method update() will take data, modify the Wikidata item and a write() call will
        then perform the actual write to Wikidata.
        :type search_only: bool
        :param item_data: A Python JSON object corresponding to the Wikidata item in wd_item_id. This can be used in
        conjunction with wd_item_id in order to provide raw data.
        :param user_agent: The user agent string to use when making http requests
        :type user_agent: str
        :param core_props: Core properties are used to retrieve a Wikidata item based on `data` if a `wd_item_id` is
        not given. This is a set of PIDs to use. If None, all Wikidata properties with a distinct values
        constraint will be used. (see: get_core_props)
        :type core_props: set
        :param core_prop_match_thresh: The proportion of core props that must match during retrieval of an item
        when the wd_item_id is not specified.
        :type core_prop_match_thresh: float
        :param debug: Enable debug output.
        :type debug: boolean
        """
        self.core_prop_match_thresh = core_prop_match_thresh
        self.wd_item_id = wd_item_id
        self.new_item = new_item
        self.mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url
        self.sparql_endpoint_url = config['SPARQL_ENDPOINT_URL'] if sparql_endpoint_url is None else sparql_endpoint_url
        self.wikibase_url = config['WIKIBASE_URL'] if wikibase_url is None else wikibase_url
        self.concept_base_uri = config['CONCEPT_BASE_URI'] if concept_base_uri is None else concept_base_uri
        self.property_constraint_pid = config['PROPERTY_CONSTRAINT_PID'] if property_constraint_pid is None else property_constraint_pid
        self.distinct_values_constraint_qid = config['DISTINCT_VALUES_CONSTRAINT_QID'] if distinct_values_constraint_qid is None else distinct_values_constraint_qid
        self.data = [] if data is None else data
        self.append_value = [] if append_value is None else append_value
        self.fast_run = fast_run
        self.fast_run_base_filter = fast_run_base_filter
        self.fast_run_use_refs = fast_run_use_refs
        self.fast_run_case_insensitive = fast_run_case_insensitive
        self.ref_handler = ref_handler
        self.global_ref_mode = global_ref_mode
        self.good_refs = good_refs
        self.keep_good_ref_statements = keep_good_ref_statements
        self.search_only = search_only
        self.item_data = item_data
        self.user_agent = config['USER_AGENT_DEFAULT'] if user_agent is None else user_agent

        self.create_new_item = False
        self.wd_json_representation = {}
        self.statements = []
        self.original_statements = []
        self.entity_metadata = {}
        self.fast_run_container = None
        self.require_write = True
        self.sitelinks = dict()
        self.lastrevid = None  # stores last revisionid after a write occurs

        self.debug = debug

        if fast_run_case_insensitive and not search_only:
            raise ValueError("If using fast run case insensitive, search_only must be set")

        if self.ref_handler:
            assert callable(self.ref_handler)
        if self.global_ref_mode == "CUSTOM" and self.ref_handler is None:
            raise ValueError("If using a custom ref mode, ref_handler must be set")

        if (core_props is None) and (self.sparql_endpoint_url not in self.DISTINCT_VALUE_PROPS):
            self.get_distinct_value_props(self.sparql_endpoint_url, self.wikibase_url, self.property_constraint_pid,
                                          self.distinct_values_constraint_qid)
        self.core_props = core_props if core_props is not None else self.DISTINCT_VALUE_PROPS[self.sparql_endpoint_url]

        try:
            self.mrh = MappingRelationHelper(self.sparql_endpoint_url)
        except Exception as e:
            # if the "equivalent property" and "mappingRelation" property are not found, we can't know what the
            # QIDs for the mapping relation types are
            self.mrh = None
            if self.debug:
                warnings.warn("mapping relation types are being ignored")

        if self.fast_run:
            self.init_fastrun()
            if self.debug:
                if self.require_write:
                    if search_only:
                        print('successful fastrun, search_only mode, we can\'t determine if data is up to date')
                    else:
                        print('successful fastrun, because no full data match you need to update the item...')
                else:
                    print('successful fastrun, no write to Wikidata required')

        if self.wd_item_id != '' and self.create_new_item == True:
            raise IDMissingError('Cannot create a new item, when a wikidata identifier is given')
        elif self.new_item == True and len(self.data) > 0:
            self.create_new_item = True
            self.__construct_claim_json()
        elif self.require_write:
            self.init_data_load()

    @classmethod
    def get_distinct_value_props(cls, sparql_endpoint_url=None, wikibase_url=None, property_constraint_pid=None,
                                 distinct_values_constraint_qid=None):
        """
        On wikidata, the default core IDs will be the properties with a distinct values constraint
        select ?p where {?p wdt:P2302 wd:Q21502410}
        See: https://www.wikidata.org/wiki/Help:Property_constraints_portal
        https://www.wikidata.org/wiki/Help:Property_constraints_portal/Unique_value
        """

        sparql_endpoint_url = config['SPARQL_ENDPOINT_URL'] if sparql_endpoint_url is None else sparql_endpoint_url
        wikibase_url = config['WIKIBASE_URL'] if wikibase_url is None else wikibase_url
        property_constraint_pid = config[
            'PROPERTY_CONSTRAINT_PID'] if property_constraint_pid is None else property_constraint_pid
        distinct_values_constraint_qid = config[
            'DISTINCT_VALUES_CONSTRAINT_QID'] if distinct_values_constraint_qid is None else distinct_values_constraint_qid

        pcpid = property_constraint_pid
        dvcqid = distinct_values_constraint_qid

        query = '''
        PREFIX wd: <{0}/entity/>
        PREFIX wdt: <{0}/prop/direct/>

        SELECT ?p WHERE {{
            ?p wdt:{1} wd:{2}
        }}
        '''.format(wikibase_url, pcpid, dvcqid)
        df = cls.execute_sparql_query(query, endpoint=sparql_endpoint_url, as_dataframe=True)
        if df.empty:
            warnings.warn("Warning: No distinct value properties found\n" +
                          "Please set P2302 and Q21502410 in your wikibase or set `core_props` manually.\n" +
                          "Continuing with no core_props")
            cls.DISTINCT_VALUE_PROPS[sparql_endpoint_url] = set()
            return None
        df.p = df.p.str.rsplit("/", 1).str[-1]
        cls.DISTINCT_VALUE_PROPS[sparql_endpoint_url] = set(df.p)

    def init_data_load(self):
        if self.wd_item_id and self.item_data:
            self.wd_json_representation = self.parse_wd_json(self.item_data)
        elif self.wd_item_id:
            self.wd_json_representation = self.get_wd_entity()
        else:
            qids_by_props = ''
            try:
                qids_by_props = self.__select_wd_item()
            except WDSearchError as e:
                self.log('ERROR', str(e))

            if qids_by_props:
                self.wd_item_id = qids_by_props
                self.wd_json_representation = self.get_wd_entity()
                self.__check_integrity()

        if not self.search_only:
            self.__construct_claim_json()
        else:
            self.data = []

    def init_fastrun(self):
        # We search if we already have a FastRunContainer with the same parameters to re-use it
        for c in WDItemEngine.fast_run_store:
            if (c.base_filter == self.fast_run_base_filter) and (c.use_refs == self.fast_run_use_refs) and \
                    (c.sparql_endpoint_url == self.sparql_endpoint_url):
                self.fast_run_container = c
                self.fast_run_container.ref_handler = self.ref_handler
                if self.debug:
                    print('Found an already existing FastRunContainer')

        if not self.fast_run_container:
            self.fast_run_container = FastRunContainer(base_filter=self.fast_run_base_filter,
                                                       base_data_type=WDBaseDataType,
                                                       engine=self.__class__,
                                                       sparql_endpoint_url=self.sparql_endpoint_url,
                                                       mediawiki_api_url=self.mediawiki_api_url,
                                                       wikibase_url=self.wikibase_url,
                                                       concept_base_uri=self.concept_base_uri,
                                                       use_refs=self.fast_run_use_refs,
                                                       ref_handler=self.ref_handler,
                                                       case_insensitive=self.fast_run_case_insensitive,
                                                       debug=self.debug)
            WDItemEngine.fast_run_store.append(self.fast_run_container)

        if not self.search_only:
            self.require_write = self.fast_run_container.write_required(self.data, append_props=self.append_value,
                                                                        cqid=self.wd_item_id)
            # set item id based on fast run data
            if not self.require_write and not self.wd_item_id:
                self.wd_item_id = self.fast_run_container.current_qid
        else:
            self.fast_run_container.load_item(self.data)
            # set item id based on fast run data
            if not self.wd_item_id:
                self.wd_item_id = self.fast_run_container.current_qid

    def rollback(self, login, bot_account=True, summary=""):
        """

        :return:
        """
        payload = {
            'action': 'rollback',
            'user': login.user,
            'pageid': self.get_pageid(),
            'token': login.rollback_token,
            'markbot': bot_account,
            'summary': summary,
            'ids': self.wd_item_id,
            'format': 'json'
        }
        headers = {
            'User-Agent': self.user_agent
        }

        json_data = self.mediawiki_api_call("POST", self.mediawiki_api_url, session=login.get_session(), headers=headers, data=payload)

        return json_data


    def get_wd_entity(self):
        """
        retrieve a WD item in json representation from Wikidata

        :rtype: dict
        :return: python complex dictionary represenation of a json
        """
        params = {
            'action': 'wbgetentities',
            'sites': 'enwiki',
            'ids': self.wd_item_id,
            'format': 'json'
        }
        headers = {
            'User-Agent': self.user_agent
        }
        json_data = self.mediawiki_api_call("GET", self.mediawiki_api_url, params=params, headers=headers)
        return self.parse_wd_json(wd_json=json_data['entities'][self.wd_item_id])

    def parse_wd_json(self, wd_json):
        """
        Parses a WD entity json and generates the datatype objects, sets self.wd_json_representation

        :param wd_json: the json of a WD entity
        :type wd_json: A Python Json representation of a WD item
        :return: returns the json representation containing 'labels', 'descriptions', 'claims', 'aliases', 'sitelinks'.
        """
        wd_data = {x: wd_json[x] for x in ('pageid', 'lastrevid', 'modified', 'labels', 'descriptions', 'claims', 'aliases') if x in wd_json}
        wd_data['sitelinks'] = dict()
        self.entity_metadata = {x: wd_json[x] for x in wd_json if x not in
                                ('labels', 'descriptions', 'claims', 'aliases', 'sitelinks')}
        self.sitelinks = wd_json.get('sitelinks', dict())
        self.pageid = wd_json.get('pageid')

        self.statements = []
        for prop in wd_data['claims']:
            for z in wd_data['claims'][prop]:
                data_type = [x for x in WDBaseDataType.__subclasses__() if x.DTYPE == z['mainsnak']['datatype']][0]
                statement = data_type.from_json(z)
                self.statements.append(statement)

        self.wd_json_representation = wd_data
        self.original_statements = copy.deepcopy(self.statements)

        return wd_data

    @staticmethod
    def get_wd_search_results(search_string='', mediawiki_api_url=None,
                              user_agent=None, max_results=500,
                              language='en', dict_id_label=False, dict_id_all_info=False):
        """
        Performs a search in WD for a certain WD search string

        :param search_string: a string which should be searched for in WD
        :type search_string: str
        :param mediawiki_api_url: Specify the mediawiki_api_url.
        :type mediawiki_api_url: str
        :param user_agent: The user agent string transmitted in the http header
        :type user_agent: str
        :param max_results: The maximum number of search results returned. Default 500
        :type max_results: int
        :param language: The language in which to perform the search. Default 'en'
        :type language: str
        :return: returns a list of QIDs found in the search and a list of labels complementary to the QIDs
        :type dict_id_label: boolean
        :return: returns a list of QIDs found in the search and a list of labels, descriptions, and wikidata urls complementary to the QIDs
        :type dict_id_all_info: boolean
        :return: function return a list with a dict of id, label, description, and url
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url
        user_agent = config['USER_AGENT_DEFAULT'] if user_agent is None else user_agent

        params = {
            'action': 'wbsearchentities',
            'language': language,
            'search': search_string,
            'format': 'json',
            'limit': 50
        }

        headers = {
            'User-Agent': user_agent
        }

        cont_count = 1
        results = []

        while cont_count > 0:
            params.update({'continue': 0 if cont_count == 1 else cont_count})

            reply = requests.get(mediawiki_api_url, params=params, headers=headers)
            reply.raise_for_status()
            search_results = reply.json()

            if search_results['success'] != 1:
                raise WDSearchError('WD search failed')
            else:
                for i in search_results['search']:
                    if dict_id_all_info: # overrides dict_id_label if both are set to True
                        description = i['description'] if 'description' in i else ""
                        url = i['url'] if 'url' in i else ""
                        results.append({'id': i['id'], 'label': i['label'], 'description': description, 'url': url})
                    elif dict_id_label:
                        results.append({'id': i['id'], 'label': i['label']})
                    else:
                        results.append(i['id'])

            if 'search-continue' not in search_results:
                cont_count = 0
            else:
                cont_count = search_results['search-continue']

            if cont_count > max_results:
                break

        return results

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
        qid_list = set()
        conflict_source = {}
        if self.mrh:
            exact_qid = self.mrh.mrt_qids['http://www.w3.org/2004/02/skos/core#exactMatch']
            mrt_pid = self.mrh.mrt_pid
        else:
            # This is a `hack` for if initializing the mapping relation helper fails. We can't determine the
            # mapping relation type PID or the exact match QID. If we set mrt_pid to "Pxxx", then no qualifier will
            # ever match it (and exact_qid will never get checked), and so what happens is exactly what would
            # happen if the statement had no mapping relation qualifiers
            exact_qid = "Q0"
            mrt_pid = "PXXX"

        for statement in self.data:
            wd_property = statement.get_prop_nr()

            # only use this statement if mapping relation type is exact, or mrt is not specified
            mrt_qualifiers = [q for q in statement.get_qualifiers() if q.get_prop_nr() == mrt_pid]
            if (len(mrt_qualifiers) == 1) and (mrt_qualifiers[0].get_value() != int(exact_qid[1:])):
                continue

            # TODO: implement special treatment when searching for date/coordinate values
            data_point = statement.get_value()
            if isinstance(data_point, tuple):
                data_point = data_point[0]

            core_props = self.core_props
            if wd_property in core_props:
                tmp_qids = set()
                # if mrt_pid is "PXXX", this is fine, because the part of the SPARQL query using it is optional
                query = statement.sparql_query.format(wb_url=self.wikibase_url, mrt_pid=mrt_pid, pid=wd_property,
                                                      value=data_point.replace("'", r"\'"))
                results = WDItemEngine.execute_sparql_query(query=query, endpoint=self.sparql_endpoint_url)

                for i in results['results']['bindings']:
                    qid = i['item_id']['value'].split('/')[-1]
                    if ('mrt' not in i) or ('mrt' in i and i['mrt']['value'].split('/')[-1] == exact_qid):
                        tmp_qids.add(qid)

                qid_list.update(tmp_qids)

                # Protocol in what property the conflict arises
                if wd_property in conflict_source:
                    conflict_source[wd_property].append(tmp_qids)
                else:
                    conflict_source[wd_property] = [tmp_qids]

                if len(tmp_qids) > 1:
                    raise ManualInterventionReqException(
                        'More than one WD item has the same property value', wd_property, tmp_qids)

        if len(qid_list) == 0:
            self.create_new_item = True
            return ''

        if self.debug:
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

        def handle_qualifiers(old_item, new_item):
            if not new_item.check_qualifier_equality:
                old_item.set_qualifiers(new_item.get_qualifiers())

        def is_good_ref(ref_block):

            if len(WDItemEngine.databases) == 0:
                WDItemEngine._init_ref_system()

            prop_nrs = [x.get_prop_nr() for x in ref_block]
            values = [x.get_value() for x in ref_block]
            good_ref = True
            prop_value_map = dict(zip(prop_nrs, values))

            # if self.good_refs has content, use these to determine good references
            if self.good_refs and len(self.good_refs) > 0:
                found_good = True
                for rblock in self.good_refs:

                    if not all([k in prop_value_map for k, v in rblock.items()]):
                        found_good = False

                    if not all([v in prop_value_map[k] for k, v in rblock.items() if v]):
                        found_good = False

                    if found_good:
                        return True

                return False

            # stated in, title, retrieved
            ref_properties = ['P248', 'P1476', 'P813']

            for v in values:
                if prop_nrs[values.index(v)] == 'P248':
                    return True
                elif v == 'P698':
                    return True

            for p in ref_properties:
                if p not in prop_nrs:
                    return False

            for ref in ref_block:
                pn = ref.get_prop_nr()
                value = ref.get_value()

                if pn == 'P248' and value not in WDItemEngine.databases and 'P854' not in prop_nrs:
                    return False
                elif pn == 'P248' and value in WDItemEngine.databases:
                    db_props = WDItemEngine.databases[value]
                    if not any([False if x not in prop_nrs else True for x in db_props]) and 'P854' not in prop_nrs:
                        return False

            return good_ref

        def handle_references(old_item, new_item):
            """
            Local function to handle references

            :param old_item: An item containing the data as currently in WD
            :type old_item: A child of WDBaseDataType
            :param new_item: An item containing the new data which should be written to WD
            :type new_item: A child of WDBaseDataType
            """
            # stated in, title, language of work, retrieved, imported from
            ref_properties = ['P248', 'P1476', 'P407', 'P813', 'P143']
            new_references = new_item.get_references()
            old_references = old_item.get_references()

            if any([z.overwrite_references for y in new_references for z in y]) \
                    or sum(map(lambda z: len(z), old_references)) == 0 \
                    or self.global_ref_mode == 'STRICT_OVERWRITE':
                old_item.set_references(new_references)

            elif self.global_ref_mode == 'STRICT_KEEP' or new_item.statement_ref_mode == 'STRICT_KEEP':
                pass

            elif self.global_ref_mode == 'STRICT_KEEP_APPEND' or new_item.statement_ref_mode == 'STRICT_KEEP_APPEND':
                old_references.extend(new_references)
                old_item.set_references(old_references)

            elif self.global_ref_mode == 'CUSTOM' or new_item.statement_ref_mode == 'CUSTOM':
                self.ref_handler(old_item, new_item)

            elif self.global_ref_mode == 'KEEP_GOOD' or new_item.statement_ref_mode == 'KEEP_GOOD':
                keep_block = [False for x in old_references]
                for count, ref_block in enumerate(old_references):
                    stated_in_value = [x.get_value() for x in ref_block if x.get_prop_nr() == 'P248']
                    if is_good_ref(ref_block):
                        keep_block[count] = True

                    new_ref_si_values = [x.get_value() if x.get_prop_nr() == 'P248' else None
                                         for z in new_references for x in z]

                    for si in stated_in_value:
                        if si in new_ref_si_values:
                            keep_block[count] = False

                refs = [x for c, x in enumerate(old_references) if keep_block[c]]
                refs.extend(new_references)
                old_item.set_references(refs)

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
                prop_pos = [x.get_prop_nr() == prop_nr for x in self.statements]
                prop_pos.reverse()
                insert_pos = len(prop_pos) - (prop_pos.index(True) if any(prop_pos) else 0)

                # If value should be appended, check if values exists, if not, append
                if prop_nr in self.append_value:
                    equal_items = [stat == x for x in prop_data]
                    if True not in equal_items:
                        self.statements.insert(insert_pos + 1, stat)
                    else:
                        # if item exists, modify rank
                        current_item = prop_data[equal_items.index(True)]
                        current_item.set_rank(stat.get_rank())
                        handle_references(old_item=current_item, new_item=stat)
                        handle_qualifiers(old_item=current_item, new_item=stat)
                    continue

                # set all existing values of a property for removal
                for x in prop_data:
                    # for deletion of single statements, do not set all others to delete
                    if hasattr(stat, 'remove'):
                        break
                    elif x.get_id() and not hasattr(x, 'retain'):
                        # keep statements with good references if keep_good_ref_statements is True
                        if self.keep_good_ref_statements:
                            if any([is_good_ref(r) for r in x.get_references()]):
                                setattr(x, 'retain', '')
                        else:
                            setattr(x, 'remove', '')

                match = []
                for i in prop_data:
                    if stat == i and hasattr(stat, 'remove'):
                        match.append(True)
                        setattr(i, 'remove', '')
                    elif stat == i:
                        match.append(True)
                        setattr(i, 'retain', '')
                        if hasattr(i, 'remove'):
                            delattr(i, 'remove')
                        handle_references(old_item=i, new_item=stat)
                        handle_qualifiers(old_item=i, new_item=stat)

                        i.set_rank(rank=stat.get_rank())
                    # if there is no value, do not add an element, this is also used to delete whole properties.
                    elif i.get_value():
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

    def update(self, data, append_value=None):
        """
        This method takes data, and modifies the Wikidata item. This works together with the data already provided via
        the constructor or if the constructor is being instantiated with search_only=True. In the latter case, this
        allows for checking the item data before deciding which new data should be written to the Wikidata item.
        The actual write to Wikidata only happens on calling of the write() method. If data has been provided already
        via the constructor, data provided via the update() method will be appended to these data.

        :param data: A list of Wikidata statment items inheriting from WDBaseDataType
        :type data: list
        :param append_value: list with Wikidata property strings where the values should only be appended,
            not overwritten.
        :type: list
        """
        assert type(data) == list

        if append_value:
            assert type(append_value) == list
            self.append_value.extend(append_value)

        self.data.extend(data)
        self.statements = copy.deepcopy(self.original_statements)

        if self.debug:
            print(self.data)

        if self.fast_run:
            self.init_fastrun()

        if self.require_write and self.fast_run:
            self.init_data_load()
            self.__construct_claim_json()
            self.__check_integrity()
        elif not self.fast_run:
            self.__construct_claim_json()
            self.__check_integrity()

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
        # all core props
        wdi_core_props = self.core_props
        # core prop statements that exist on the item
        cp_statements = [x for x in self.statements if x.get_prop_nr() in wdi_core_props]
        item_core_props = set(x.get_prop_nr() for x in cp_statements)
        # core prop statements we are loading
        cp_data = [x for x in self.data if x.get_prop_nr() in wdi_core_props]

        # compare the claim values of the currently loaded QIDs to the data provided in self.data
        # this is the number of core_ids in self.data that are also on the item
        count_existing_ids = len([x for x in self.data if x.get_prop_nr() in item_core_props])

        core_prop_match_count = 0
        for new_stat in self.data:
            for stat in self.statements:
                if (new_stat.get_prop_nr() == stat.get_prop_nr()) and (new_stat.get_value() == stat.get_value()) \
                        and (new_stat.get_prop_nr() in item_core_props):
                    core_prop_match_count += 1

        if core_prop_match_count < count_existing_ids * self.core_prop_match_thresh:
            existing_core_pv = defaultdict(set)
            for s in cp_statements:
                existing_core_pv[s.get_prop_nr()].add(s.get_value())
            new_core_pv = defaultdict(set)
            for s in cp_data:
                new_core_pv[s.get_prop_nr()].add(s.get_value())
            nomatch_existing = {k: v - new_core_pv[k] for k, v in existing_core_pv.items()}
            nomatch_existing = {k: v for k, v in nomatch_existing.items() if v}
            nomatch_new = {k: v - existing_core_pv[k] for k, v in new_core_pv.items()}
            nomatch_new = {k: v for k, v in nomatch_new.items() if v}
            raise CorePropIntegrityException('Retrieved item ({}) does not match provided core IDs. '
                                             'Matching count {}, non-matching count {}. '
                                             .format(self.wd_item_id, core_prop_match_count,
                                                     count_existing_ids - core_prop_match_count) +
                                             'existing unmatched core props: {}. '.format(nomatch_existing) +
                                             'statement unmatched core props: {}.'.format(nomatch_new))
        else:
            return True

    def get_pageid(self):
        """
        Returns the pageid of a Wikidata item

        :return:
        """
        return self.wd_json_representation['pageid']

    def get_label(self, lang='en'):
        """
        Returns the label for a certain language

        :param lang:
        :type lang: str
        :return: returns the label in the specified language, an empty string if the label does not exist
        """
        if self.fast_run:
            return list(self.fast_run_container.get_language_data(self.wd_item_id, lang, 'label'))[0]
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
        if self.fast_run and not self.require_write:
            self.require_write = self.fast_run_container.check_language_data(qid=self.wd_item_id,
                                                                             lang_data=[label], lang=lang,
                                                                             lang_data_type='label')
            if self.require_write:
                self.init_data_load()
            else:
                return

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
        if self.fast_run:
            return list(self.fast_run_container.get_language_data(self.wd_item_id, lang, 'aliases'))

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
        if self.fast_run and not self.require_write:
            self.require_write = self.fast_run_container.check_language_data(qid=self.wd_item_id,
                                                                             lang_data=aliases, lang=lang,
                                                                             lang_data_type='aliases')
            if self.require_write:
                self.init_data_load()
            else:
                return

        if 'aliases' not in self.wd_json_representation:
            self.wd_json_representation['aliases'] = {}

        if not append or lang not in self.wd_json_representation['aliases']:
            self.wd_json_representation['aliases'][lang] = []

        for alias in aliases:
            found = False
            for current_aliases in self.wd_json_representation['aliases'][lang]:
                if alias.strip().lower() != current_aliases['value'].strip().lower():
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
        if self.fast_run:
            return list(self.fast_run_container.get_language_data(self.wd_item_id, lang, 'description'))[0]
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
        if self.fast_run and not self.require_write:
            self.require_write = self.fast_run_container.check_language_data(qid=self.wd_item_id,
                                                                             lang_data=[description], lang=lang,
                                                                             lang_data_type='description')
            if self.require_write:
                self.init_data_load()
            else:
                return

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
        sitelink = {
            'site': site,
            'title': title,
            'badges': badges
        }
        self.wd_json_representation['sitelinks'][site] = sitelink
        self.sitelinks[site] = sitelink

    def get_sitelink(self, site):
        """
        A method to access the interwiki links in the json.model

        :param site: The Wikipedia site the interwiki/sitelink should be returned for
        :return: The interwiki/sitelink string for the specified Wikipedia will be returned.
        """
        if site in self.sitelinks:
            return self.sitelinks[site]
        else:
            return None

    def write(self, login, bot_account=True, edit_summary='', entity_type='item', property_datatype='string',
              max_retries=1000, retry_after=60):
        """
        Writes the WD item Json to WD and after successful write, updates the object with new ids and hashes generated
        by WD. For new items, also returns the new QIDs.

        :param login: a instance of the class PBB_login which provides edit-cookies and edit-tokens
        :param bot_account: Tell the Wikidata API whether the script should be run as part of a bot account or not.
        :type bot_account: bool
        :param edit_summary: A short (max 250 characters) summary of the purpose of the edit. This will be displayed as
            the revision summary of the Wikidata item.
        :type edit_summary: str
        :param entity_type: Decides wether the object will become an item (default) or a property (with 'property')
        :type entity_type: str
        :param property_datatype: When payload_type is 'property' then this parameter set the datatype for the property
        :type property_datatype: str
        :param max_retries: If api request fails due to rate limiting, maxlag, or readonly mode, retry up to
        `max_retries` times
        :type max_retries: int
        :param retry_after: Number of seconds to wait before retrying request (see max_retries)
        :type retry_after: int
        :return: the WD QID on sucessful write
        """
        if not self.require_write:
            return self.wd_item_id

        if entity_type == 'property':
            self.wd_json_representation['datatype'] = property_datatype
            if 'sitelinks' in self.wd_json_representation:
                del self.wd_json_representation['sitelinks']

        payload = {
            'action': 'wbeditentity',
            'data': json.JSONEncoder().encode(self.wd_json_representation),
            'format': 'json',
            'token': login.get_edit_token(),
            'summary': edit_summary,
            'maxlag': config['MAXLAG']
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8'
        }

        if bot_account:
            payload.update({'bot': ''})

        if self.create_new_item:
            payload.update({u'new': entity_type})
        else:
            payload.update({u'id': self.wd_item_id})

        try:
            json_data = self.mediawiki_api_call('POST', self.mediawiki_api_url, session=login.get_session(),
                                                max_retries=max_retries, retry_after=retry_after,
                                                headers=headers, data=payload)

            if 'error' in json_data and 'messages' in json_data['error']:
                error_msg_names = set(x.get('name') for x in json_data["error"]['messages'])
                if 'wikibase-validator-label-with-description-conflict' in error_msg_names:
                    raise NonUniqueLabelDescriptionPairError(json_data)
                else:
                    raise WDApiError(json_data)
            elif 'error' in json_data.keys():
                raise WDApiError(json_data)
        except Exception:
            print('Error while writing to Wikidata')
            raise

        # after successful write, update this object with latest json, QID and parsed data types.
        self.create_new_item = False
        self.wd_item_id = json_data['entity']['id']
        self.parse_wd_json(wd_json=json_data['entity'])
        self.data = []
        if "success" in json_data and "entity" in json_data and "lastrevid" in json_data["entity"]:
            self.lastrevid = json_data["entity"]["lastrevid"]
        if "success" in json_data and "entity" in json_data and "pageid" in json_data["entity"]:
            self.pageid = json_data["entity"]["pageid"]
        return self.wd_item_id

    def check_entity_schema(self, eid=None, entity_schema_repo=None, output='confirm', max_steps=1):
        """
                Static method which can be used to check for conformance of a Wikidata item to an EntitySchema any SPARQL query
                :param qid: The URI prefixes required for an endpoint, default is the Wikidata specific prefixes
                :param eid: The EntitySchema identifier from Wikidata
                :param sparql_endpoint_url: The URL string for the SPARQL endpoint. Default is the URL for the Wikidata SPARQL endpoint
                :param output: results of a test of conformance on a given shape expression
                :return: The results of the query are returned in string format
        """
        rdfdata = wdi_rdf.WDqidRDFEngine(qid=self.wd_item_id, json_data=self.get_wd_json_representation(), max_steps=max_steps, current_step = 0).rdf_item

        entity_schema_repo = config["ENTITY_SCHEMA_REPO"] if entity_schema_repo is None else entity_schema_repo
        schema = requests.get(entity_schema_repo+eid).text

        for result in ShExEvaluator(rdf=rdfdata, schema=schema, focus=config["CONCEPT_BASE_URI"] + self.wd_item_id).evaluate():
            shex_result = dict()
            if result.result:
                shex_result["result"] = True
            else:
                shex_result["result"] = False
            shex_result["reason"] = result.reason
            shex_result["focus"] = result.focus

        if output == "confirm":
            return shex_result["result"]
        elif output == "reason":
            return shex_result["reason"]
        else:
            return shex_result

    @staticmethod
    def mediawiki_api_call(method, mediawiki_api_url=None,
                           session=None, max_retries=1000, retry_after=60, **kwargs):
        """
        :param method: 'GET' or 'POST'
        :param mediawiki_api_url:
        :param session: If a session is passed, it will be used. Otherwise a new requests session is created
        :param max_retries: If api request fails due to rate limiting, maxlag, or readonly mode, retry up to
        `max_retries` times
        :type max_retries: int
        :param retry_after: Number of seconds to wait before retrying request (see max_retries)
        :type retry_after: int
        :param kwargs: Passed to requests.request
        :return:
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url

        response = None
        session = session if session else requests.session()
        for n in range(max_retries):
            try:
                response = session.request(method, mediawiki_api_url, **kwargs)
            except requests.exceptions.ConnectionError as e:
                print("Connection error: {}. Sleeping for {} seconds.".format(e, retry_after))
                time.sleep(retry_after)
                continue
            if response.status_code == 503:
                print("service unavailable. sleeping for {} seconds".format(retry_after))
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            json_data = response.json()
            """
            wikidata api response has code = 200 even if there are errors.
            rate limit doesn't return HTTP 429 either. may in the future
            https://phabricator.wikimedia.org/T172293
            """
            if 'error' in json_data:
                # rate limiting
                error_msg_names = set()
                if 'messages' in json_data['error']:
                    error_msg_names = set(x.get('name') for x in json_data["error"]['messages'])
                if 'actionthrottledtext' in error_msg_names:
                    sleep_sec = int(response.headers.get('retry-after', retry_after))
                    print("{}: rate limited. sleeping for {} seconds".format(datetime.datetime.utcnow(), sleep_sec))
                    time.sleep(sleep_sec)
                    continue

                # maxlag
                if 'code' in json_data['error'] and json_data['error']['code'] == 'maxlag':
                    sleep_sec = json_data['error'].get('lag', retry_after)
                    print("{}: maxlag. sleeping for {} seconds".format(datetime.datetime.utcnow(), sleep_sec))
                    time.sleep(sleep_sec)
                    continue

                # readonly
                if 'code' in json_data['error'] and json_data['error']['code'] == 'readonly':
                    print('Wikidata currently is in readonly mode, waiting for {} seconds'.format(retry_after))
                    time.sleep(retry_after)
                    continue

            # there is no error or waiting. break out of this loop and parse response
            break
        else:
            # the first time I've ever used for - else!!
            # else executes if the for loop completes normally. i.e. does not encouter a `break`
            # in this case, that means it tried this api call 10 times
            raise WDApiError(response.json() if response else dict())

        return json_data

    @classmethod
    def setup_logging(cls, log_dir="./logs", log_name=None, header=None, names=None,
                      delimiter=";", logger_name='WD_logger'):
        """
        A static method which initiates log files compatible to .csv format, allowing for easy further analysis.

        :param log_dir: allows for setting relative or absolute path for logging, default is ./logs.
        :type log_dir: str
        :param log_name: File name of log file to be written. e.g. "WD_bot_run-20160204.log". Default is "WD_bot_run"
        and a timestamp of the current time
        :type log_name: str
        :param header: Log file will be prepended with header if given
        :type header: str
        :param names: Column names for the log file
        :type names: list
        :param delimiter: Log file will be delimited with `delimiter`
        :type delimiter: str
        """
        names = ["level", "timestamp", "external_id", "external_id_prop", "wdid", "msg", "msg_type",
                 "revid"] if names is None else names

        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        if not log_name:
            run_id = time.strftime('%Y%m%d_%H:%M', time.localtime())
            log_name = "WD_bot_run-{}.log".format(run_id)

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)

        log_file_name = os.path.join(log_dir, log_name)

        file_handler = logging.FileHandler(log_file_name, mode='a')
        file_handler.setLevel(logging.DEBUG)

        fmt = '%(levelname)s{delimiter}%(asctime)s{delimiter}%(message)s'.format(delimiter=delimiter)
        if header:
            header = header if header.startswith("#") else "#" + header
            header += "\n" + delimiter.join(names)
            formatter = FormatterWithHeader(header, fmt=fmt, datefmt='%m/%d/%Y %H:%M:%S')
        else:
            formatter = FormatterWithHeader(delimiter.join(names), fmt=fmt, datefmt='%m/%d/%Y %H:%M:%S')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        cls.logger = logger

    @classmethod
    def log(cls, level, message):
        """
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
        if cls.logger is None:
            cls.setup_logging()

        log_levels = {'DEBUG': logging.DEBUG, 'ERROR': logging.ERROR, 'INFO': logging.INFO, 'WARNING': logging.WARNING,
                      'CRITICAL': logging.CRITICAL}

        cls.logger.log(level=log_levels[level], msg=message)

    @classmethod
    def generate_item_instances(cls, items, mediawiki_api_url=None, login=None,
                                user_agent=None):
        """
        A method which allows for retrieval of a list of Wikidata items or properties. The method generates a list of
        tuples where the first value in the tuple is the QID or property ID, whereas the second is the new instance of
        WDItemEngine containing all the data of the item. This is most useful for mass retrieval of WD items.

        :param items: A list of QIDs or property IDs
        :type items: list
        :param mediawiki_api_url: The MediaWiki url which should be used
        :type mediawiki_api_url: str
        :param login: An object of type WDLogin, which holds the credentials/session cookies required for >50 item bulk
            retrieval of items.
        :type login: wdi_login.WDLogin
        :return: A list of tuples, first value in the tuple is the QID or property ID string, second value is the
            instance of WDItemEngine with the corresponding item data.
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url
        user_agent = config['USER_AGENT_DEFAULT'] if user_agent is None else user_agent

        assert type(items) == list

        url = mediawiki_api_url
        params = {
            'action': 'wbgetentities',
            'ids': '|'.join(items),
            'format': 'json'
        }
        headers = {
            'User-Agent': user_agent
        }

        if login:
            reply = login.get_session().get(url, params=params, headers=headers)
        else:
            reply = requests.get(url, params=params)

        item_instances = []
        for qid, v in reply.json()['entities'].items():
            ii = cls(wd_item_id=qid, item_data=v)
            ii.mediawiki_api_url = mediawiki_api_url
            item_instances.append((qid, ii))

        return item_instances

    @staticmethod
    @wdi_backoff()
    def execute_sparql_query(query, prefix=None, endpoint=None,
                             user_agent=None, as_dataframe=False, max_retries=1000, retry_after=60):
        """
        Static method which can be used to execute any SPARQL query

        :param prefix: The URI prefixes required for an endpoint, default is the Wikidata specific prefixes
        :param query: The actual SPARQL query string
        :param endpoint: The URL string for the SPARQL endpoint. Default is the URL for the Wikidata SPARQL endpoint
        :param user_agent: Set a user agent string for the HTTP header to let the WDQS know who you are.
        :param as_dataframe: Return result as pandas dataframe
        :type user_agent: str
        :param max_retries: The number time this function should retry in case of header reports.
        :param retry_after: the number of seconds should wait upon receiving either an error code or the WDQS is not reachable.
        :return: The results of the query are returned in JSON format
        """

        sparql_endpoint_url = config['SPARQL_ENDPOINT_URL'] if endpoint is None else endpoint
        user_agent = config['USER_AGENT_DEFAULT'] if user_agent is None else user_agent

        if prefix:
            query = prefix + '\n' + query

        params = {
            'query': '#Tool: wdi_core fastrun\n' + query,
            'format': 'json'
        }

        headers = {
            'Accept': 'application/sparql-results+json',
            'User-Agent': user_agent
        }
        response = None

        for n in range(max_retries):
            try:
                response = requests.post(sparql_endpoint_url, params=params, headers=headers)
            except requests.exceptions.ConnectionError as e:
                print("Connection error: {}. Sleeping for {} seconds.".format(e, retry_after))
                time.sleep(retry_after)
                continue
            if response.status_code == 503:
                print("service unavailable. sleeping for {} seconds".format(retry_after))
                time.sleep(retry_after)
                continue
            if response.status_code == 429:
                if "retry-after" in response.headers.keys():
                    retry_after = response.headers["retry-after"]
                print("service unavailable. sleeping for {} seconds".format(retry_after))
                time.sleep(retry_after)
                continue
            response.raise_for_status()
            results = response.json()

            if as_dataframe:
                return WDItemEngine._sparql_query_result_to_df(results)
            else:
                return results

    @staticmethod
    def _sparql_query_result_to_df(results):

        def parse_value(item):
            if item.get("datatype") == "http://www.w3.org/2001/XMLSchema#decimal":
                return float(item['value'])
            if item.get("datatype") == "http://www.w3.org/2001/XMLSchema#integer":
                return int(item['value'])
            if item.get("datatype") == "http://www.w3.org/2001/XMLSchema#dateTime":
                return datetime.datetime.strptime(item['value'], '%Y-%m-%dT%H:%M:%SZ')
            return item['value']

        results = results['results']['bindings']
        results = [{k: parse_value(v) for k, v in item.items()} for item in results]
        df = pd.DataFrame(results)
        return df

    @staticmethod
    def get_linked_by(qid, mediawiki_api_url=None):
        """
            :param qid: Wikidata identifier to which other wikidata items link
            :param mediawiki_api_url: default to wikidata's api, but can be changed to any wikibase
            :return:
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url

        linkedby = []
        whatlinkshere = json.loads(requests.get(
            mediawiki_api_url + "?action=query&list=backlinks&format=json&bllimit=500&bltitle=" + qid).text)
        for link in whatlinkshere["query"]["backlinks"]:
            if link["title"].startswith("Q"):
                linkedby.append(link["title"])
        while 'continue' in whatlinkshere.keys():
            whatlinkshere = json.loads(requests.get(
                mediawiki_api_url + "?action=query&list=backlinks&blcontinue=" +
                whatlinkshere['continue']['blcontinue'] + "&format=json&bllimit=50&bltitle=" + "Q42").text)
            for link in whatlinkshere["query"]["backlinks"]:
                if link["title"].startswith("Q"):
                    linkedby.append(link["title"])
        return (linkedby)

    @staticmethod
    def get_rdf(qid, format="turtle", mediawiki_api_url=None):
        """
            :param qid: Wikidata identifier to extract the RDF of
            :format RDF from to return takes (turtle, ntriples, rdfxml, see https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.html)
            :param mediawiki_api_url: default to wikidata's api, but can be changed to any wikibase
            :return:
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url

        localcopy = Graph()
        localcopy.parse(config["CONCEPT_BASE_URI"] + qid + ".ttl")
        return (localcopy.serialize(format=format))

    @staticmethod
    def merge_items(from_id, to_id, login_obj, mediawiki_api_url=None,
                    ignore_conflicts='', user_agent=None):
        """
        A static method to merge two Wikidata items

        :param from_id: The QID which should be merged into another item
        :type from_id: string with 'Q' prefix
        :param to_id: The QID into which another item should be merged
        :type to_id: string with 'Q' prefix
        :param login_obj: The object containing the login credentials and cookies
        :type login_obj: instance of PBB_login.WDLogin
        :param mediawiki_api_url: The MediaWiki url which should be used
        :type mediawiki_api_url: str
        :param ignore_conflicts: A string with the values 'description', 'statement' or 'sitelink', separated
                by a pipe ('|') if using more than one of those.
        :type ignore_conflicts: str
        """

        url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url
        user_agent = config['USER_AGENT_DEFAULT'] if user_agent is None else user_agent

        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'charset': 'utf-8',
            'User-Agent': user_agent
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
            # TODO: should we retry this?
            merge_reply = requests.post(url=url, data=params, headers=headers, cookies=login_obj.get_edit_cookie())
            merge_reply.raise_for_status()

            if 'error' in merge_reply.json():
                raise MergeError(merge_reply.json())

        except requests.HTTPError as e:
            print(e)
            # TODO: should we return this?
            return {'error': 'HTTPError'}

        return merge_reply.json()

    # TODO: adapt this function for wikibase (if possible)
    @classmethod
    def _init_ref_system(cls, sparql_endpoint_url=None):
        db_query = '''
        SELECT DISTINCT ?db ?wd_prop WHERE {
            {?db wdt:P31 wd:Q2881060 . } UNION
            {?db wdt:P31 wd:Q4117139 . } UNION
            {?db wdt:P31 wd:Q8513 . } UNION
            {?db wdt:P31 wd:Q324254 .}

            OPTIONAL {
              ?db wdt:P1687 ?wd_prop .
            }
        }'''

        for x in cls.execute_sparql_query(db_query, endpoint=sparql_endpoint_url)['results']['bindings']:
            db_qid = x['db']['value'].split('/')[-1]
            if db_qid not in cls.databases:
                cls.databases.update({db_qid: []})

            if 'wd_prop' in x:
                cls.databases[db_qid].append(x['wd_prop']['value'].split('/')[-1])

    @staticmethod
    def delete_item(item, reason, login, mediawiki_api_url=None, user_agent=None):
        """
        Takes a list of items and posts them for deletion by Wikidata moderators, appends at the end of the deletion
        request page.

        :param item: a QID which should be deleted
        :type item: string
        :param reason: short text about the reason for the deletion request
        :type reason: str
        :param login: A WDI login object which contains username and password the edit should be performed with.
        :type login: wdi_login.WDLogin
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url
        user_agent = config['USER_AGENT_DEFAULT'] if user_agent is None else user_agent

        params = {
            'action': 'delete',
            'title': 'Item:' + item,
            'reason': reason,
            'token': login.get_edit_token(),
            'format': 'json'
        }
        headers = {
            'User-Agent': user_agent
        }
        r = requests.post(url=mediawiki_api_url, data=params, cookies=login.get_edit_cookie(), headers=headers)
        print(r.json())

    @staticmethod
    def delete_statement(statement_id, revision, login, mediawiki_api_url='https://www.wikidata.org/w/api.php',
                         user_agent=config['USER_AGENT_DEFAULT']):
        params = {
            'action': 'wbremoveclaims',
            'claim': statement_id,
            'token': login.get_edit_token(),
            'baserevid': revision,
            'bot': True,
            'format': 'json'
        }
        headers = {
            'User-Agent': user_agent
        }
        r = requests.post(url=mediawiki_api_url, data=params, cookies=login.get_edit_cookie(), headers=headers)
        print(r.json())

    ## References
    @classmethod
    def count_references(self, prop_id, user_agent=config['USER_AGENT_DEFAULT']):
        counts = dict()
        for claim in self.get_wd_json_representation()["claims"][prop_id]:
            counts[claim["id"]] = len(claim["references"])
        return counts

    @classmethod
    def get_reference_properties(self, prop_id, user_agent=config['USER_AGENT_DEFAULT']):
        references = []
        for statements in self.get_wd_json_representation()["claims"][prop_id]:
            for reference in statements["references"]:
                references.append(reference["snaks"].keys())
        return references

    @classmethod
    def get_qualifier_properties(self, prop_id, user_agent=config['USER_AGENT_DEFAULT']):
        qualifiers = []
        for statements in self.get_wd_json_representation()["claims"][prop_id]:
            for reference in statements["qualifiers"]:
                qualifiers.append(reference["snaks"].keys())
        return qualifiers

    @classmethod
    def wikibase_item_engine_factory(cls, mediawiki_api_url=config['MEDIAWIKI_API_URL'],
                                     sparql_endpoint_url=config['SPARQL_ENDPOINT_URL'], name='LocalItemEngine'):
        """
        Helper function for creating a WDItemEngine class with arguments set for a different Wikibase instance than
        Wikidata.

        :param mediawiki_api_url: Mediawiki api url. For wikidata, this is: 'https://www.wikidata.org/w/api.php'
        :param sparql_endpoint_url: sparql endpoint url. For wikidata, this is: 'https://query.wikidata.org/sparql'
        :param name: name of the resulting class
        :return: a subclass of WDItemEngine with the mediawiki_api_url and sparql_endpoint_url arguments set
        """

        mediawiki_api_url = config['MEDIAWIKI_API_URL'] if mediawiki_api_url is None else mediawiki_api_url
        sparql_endpoint_url = config['SPARQL_ENDPOINT_URL'] if sparql_endpoint_url is None else sparql_endpoint_url

        class SubCls(cls):
            def __init__(self, *args, **kwargs):
                kwargs['mediawiki_api_url'] = mediawiki_api_url
                kwargs['sparql_endpoint_url'] = sparql_endpoint_url
                super(SubCls, self).__init__(*args, **kwargs)

        SubCls.__name__ = name
        return SubCls

    """A mixin implementing a simple __repr__."""

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs="\r\n\t ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )


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

                        for prop_ref in jsn:
                            ref_class = self.get_class_representation(prop_ref)
                            ref_class.is_reference = True
                            ref_class.snak_type = prop_ref['snaktype']
                            ref_class.set_hash(ref_hash)

                            self.references[count].append(copy.deepcopy(ref_class))

                            # print(self.references)
            if 'qualifiers' in json_representation:
                for prop in json_representation['qualifiers-order']:
                    for qual in json_representation['qualifiers'][prop]:
                        qual_hash = ''
                        if 'hash' in qual:
                            qual_hash = qual['hash']

                        qual_class = self.get_class_representation(qual)
                        qual_class.is_qualifier = True
                        qual_class.snak_type = qual['snaktype']
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

    # example sparql query
    """
    SELECT * WHERE {
      ?item_id p:P492 ?s .
      ?s ps:P492 '614212' .
      OPTIONAL {?s pq:P4390 ?mrt}
    }"""

    sparql_query = '''
        PREFIX wd: <{wb_url}/entity/>
        PREFIX wdt: <{wb_url}/prop/direct/>
        PREFIX p: <{wb_url}/prop/>
        PREFIX ps: <{wb_url}/prop/statement/>
        PREFIX pq: <{wb_url}/prop/qualifier/>
        SELECT * WHERE {{
          ?item_id p:{pid} ?s .
          ?s ps:{pid} '{value}' .
          OPTIONAL {{?s pq:{mrt_pid} ?mrt}}
        }}
    '''

    def __init__(self, value, snak_type, data_type, is_reference, is_qualifier, references, qualifiers, rank, prop_nr,
                 check_qualifier_equality):
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
        if not references:
            self.references = []
        else:
            self.references = references
        self.qualifiers = qualifiers
        self.is_reference = is_reference
        self.is_qualifier = is_qualifier
        self.rank = rank
        self.check_qualifier_equality = check_qualifier_equality

        self._statement_ref_mode = 'KEEP_GOOD'

        if not references:
            self.references = list()
        if not self.qualifiers:
            self.qualifiers = list()

        if type(prop_nr) is int:
            self.prop_nr = 'P' + str(prop_nr)
        elif prop_nr.startswith('P'):
            self.prop_nr = prop_nr
        else:
            self.prop_nr = 'P' + prop_nr

        # Flag to allow complete overwrite of existing references for a value
        self._overwrite_references = False

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
        if (len(self.references) > 0 or len(self.qualifiers) > 0) and (self.is_qualifier or self.is_reference):
            raise ValueError('Qualifiers or references cannot have references')

    def has_equal_qualifiers(self, other):
        # check if the qualifiers are equal with the 'other' object
        equal_qualifiers = True
        self_qualifiers = copy.deepcopy(self.get_qualifiers())
        other_qualifiers = copy.deepcopy(other.get_qualifiers())

        if len(self_qualifiers) != len(other_qualifiers):
            equal_qualifiers = False
        else:
            flg = [False for x in range(len(self_qualifiers))]
            for count, i in enumerate(self_qualifiers):
                for q in other_qualifiers:
                    if i == q:
                        flg[count] = True
            if not all(flg):
                equal_qualifiers = False

        return equal_qualifiers

    def __eq__(self, other):
        equal_qualifiers = self.has_equal_qualifiers(other)
        equal_values = self.get_value() == other.get_value() and self.get_prop_nr() == other.get_prop_nr()

        if not (self.check_qualifier_equality and other.check_qualifier_equality) and equal_values:
            return True
        elif equal_values and equal_qualifiers:
            return True
        else:
            return False

    def __ne__(self, other):
        equal_qualifiers = self.has_equal_qualifiers(other)
        nonequal_values = self.get_value() != other.get_value() or self.get_prop_nr() != other.get_prop_nr()

        if not (self.check_qualifier_equality and other.check_qualifier_equality) and nonequal_values:
            return True
        if nonequal_values or not equal_qualifiers:
            return True
        else:
            return False

    # DEPRECATED: the property overwrite_references will be deprecated ASAP and should not be used
    @property
    def overwrite_references(self):
        return self._overwrite_references

    @overwrite_references.setter
    def overwrite_references(self, value):
        assert (value is True or value is False)
        print('DEPRECATED!!! Calls to overwrite_references should not be used')
        self._overwrite_references = value

    @property
    def statement_ref_mode(self):
        return self._statement_ref_mode

    @statement_ref_mode.setter
    def statement_ref_mode(self, value):
        """Set the reference mode for a statement, always overrides the global reference state."""
        valid_values = ['STRICT_KEEP', 'STRICT_KEEP_APPEND', 'STRICT_OVERWRITE', 'KEEP_GOOD', 'CUSTOM']
        if value not in valid_values:
            raise ValueError('Not an allowed reference mode, allowed values {}'.format(' '.join(valid_values)))

        self._statement_ref_mode = value

    def get_value(self):
        return self.value

    def set_value(self, value):
        if value is None and self.snak_type not in {'novalue', 'somevalue'}:
            raise ValueError("If 'value' is None, snak_type must be novalue or somevalue")
        if self.snak_type in {'novalue', 'somevalue'}:
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

                    # if more reference values with the same property number, append to its specific property list.
                    if prop_nr in snaks:
                        snaks[prop_nr].append(tmp_json[prop_nr][0])
                    else:
                        snaks.update(tmp_json)
                    snaks_order.append(prop_nr)

            qual_json = {}
            qualifiers_order = []
            for qual in self.qualifiers:
                prop_nr = qual.get_prop_nr()
                if prop_nr in qual_json:
                    qual_json[prop_nr].append(qual.get_json_representation()[prop_nr][0])
                else:
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
                   qualifiers=[], rank='', prop_nr=prop_nr, check_qualifier_equality=True)

    def equals(self, that, include_ref=False, fref=None):
        """
        Tests for equality of two statements.
        If comparing references, the order of the arguments matters!!!
        self is the current statement, the next argument is the new statement.
        Allows passing in a function to use to compare the references 'fref'. Default is equality.
        fref accepts two arguments 'oldrefs' and 'newrefs', each of which are a list of references,
        where each reference is a list of statements
        """
        if not include_ref:
            # return the result of WDBaseDataType.__eq__, which is testing for equality of value and qualifiers
            return self == that
        if include_ref and self != that:
            return False
        if include_ref and fref is None:
            fref = WDBaseDataType.refs_equal
        return fref(self, that)

    @staticmethod
    def refs_equal(olditem, newitem):
        """
        tests for exactly identical references
        """
        oldrefs = olditem.references
        newrefs = newitem.references

        ref_equal = lambda oldref, newref: True if (len(oldref) == len(newref)) and all(
            x in oldref for x in newref) else False
        if len(oldrefs) == len(newrefs) and all(
                any(ref_equal(oldref, newref) for oldref in oldrefs) for newref in newrefs):
            return True
        else:
            return False

    """A mixin implementing a simple __repr__."""

    def __repr__(self):
        return "<{klass} @{id:x} {attrs}>".format(
            klass=self.__class__.__name__,
            id=id(self) & 0xFFFFFF,
            attrs=" ".join("{}={!r}".format(k, v) for k, v in self.__dict__.items()),
        )


class WDString(WDBaseDataType):
    """
    Implements the Wikidata data type 'string'
    """
    DTYPE = 'string'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
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
                                       qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                       check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
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


class WDMath(WDBaseDataType):
    """
    Implements the Wikidata data type 'math' for mathematical formula in TEX format
    """
    DTYPE = 'math'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
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

        super(WDMath, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                                     is_qualifier=is_qualifier, references=references, qualifiers=qualifiers,
                                     rank=rank, prop_nr=prop_nr, check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        self.value = value

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

        super(WDMath, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])

class WDEDTF(WDBaseDataType):
    """
    Implements the data type for Extended Date/Time Format (EDTF) extension.
    More info: https://github.com/ProfessionalWiki/WikibaseEdtf
    """
    DTYPE = 'edtf'
    sparql_query = '''
        SELECT * WHERE {{
          ?item_id <{wb_url}/prop/{pid}> ?s .
          ?s <{wb_url}/prop/statement/{pid}> '{value}'^^xsd:edtf .
        }}
    '''

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                qualifiers=None, rank='normal', check_qualifier_equality=True):
        """
        Constructor, calls the superclass BaseDataType
        :param value: Value using the Extended Date/Time Format (EDTF)
        :type value: str with a 'P' prefix, followed by several digits or only the digits without the 'P' prefix
        :param prop_nr: The property number for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param is_reference: Whether this snak is a reference
        :type is_reference: boolean
        :param is_qualifier: Whether this snak is a qualifier
        :type is_qualifier: boolean
        :param snak_type: The snak type, either 'value', 'somevalue' or 'novalue'
        :type snak_type: str
        :param references: List with reference objects
        :type references: A data type with subclass of BaseDataType
        :param qualifiers: List with qualifier objects
        :type qualifiers: A data type with subclass of BaseDataType
        :param rank: rank of a snak with value 'preferred', 'normal' or 'deprecated'
        :type rank: str
        """

        super(WDEDTF, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                    is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                    qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                    check_qualifier_equality=check_qualifier_equality)

        self.set_value(value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        self.value = value

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

        super(WDEDTF, self).set_value(value=self.value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])

class WDExternalID(WDBaseDataType):
    """
    Implements the Wikidata data type 'external-id'
    """
    DTYPE = 'external-id'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
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

        super(WDExternalID, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                           is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                           qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                           check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        self.value = value

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

        super(WDExternalID, self).set_value(value=value)

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
        PREFIX wd: <{wb_url}/entity/>
        PREFIX wdt: <{wb_url}/prop/direct/>
        PREFIX p: <{wb_url}/prop/>
        PREFIX ps: <{wb_url}/prop/statement/>
        PREFIX pq: <{wb_url}/prop/qualifier/>
        SELECT * WHERE {{
          ?item_id p:{pid} ?s .
          ?s ps:{pid} wd:Q{value} .
          OPTIONAL {{?s pq:{mrt_pid} ?mrt}}
        }}
    '''

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
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
                                       qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                       check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, (str, int)) or value is None, \
            "Expected str or int, found {} ({})".format(type(value), value)
        if value is None:
            self.value = value
        elif isinstance(value, int):
            self.value = value
        elif value.startswith("Q"):
            pattern = re.compile('[0-9]+')
            matches = pattern.match(value[1:])

            if len(value[1:]) == len(matches.group(0)):
                self.value = int(value[1:])
            else:
                raise ValueError('Invalid WD item ID, format must be "Q[0-9]*"')
        else:
            raise ValueError('Invalid WD item ID, format must be "Q[0-9]*"')

        self.json_representation['datavalue'] = {
            'value': {
                'entity-type': 'item',
                'numeric-id': self.value,
                'id': 'Q{}'.format(self.value)
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
        PREFIX wd: <{wb_url}/entity/>
        PREFIX wdt: <{wb_url}/prop/direct/>
        PREFIX p: <{wb_url}/prop/>
        PREFIX ps: <{wb_url}/prop/statement/>
        PREFIX pq: <{wb_url}/prop/qualifier/>
        SELECT * WHERE {{
          ?item_id p:{pid} ?s .
          ?s ps:{pid} wd:P{value} .
          OPTIONAL {{?s pq:{mrt_pid} ?mrt}}
        }}
    '''

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
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
                                         qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                         check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, (str, int)) or value is None, \
            "Expected str or int, found {} ({})".format(type(value), value)
        if value is None:
            self.value = value
        elif isinstance(value, int):
            self.value = value
        elif value.startswith("P"):
            pattern = re.compile('[0-9]+')
            matches = pattern.match(value[1:])

            if len(value[1:]) == len(matches.group(0)):
                self.value = int(value[1:])
            else:
                raise ValueError('Invalid WD property ID, format must be "P[0-9]*"')
        else:
            raise ValueError('Invalid WD property ID, format must be "P[0-9]*"')

        self.json_representation['datavalue'] = {
            'value': {
                'entity-type': 'property',
                'numeric-id': self.value,
                'id': 'P{}'.format(self.value)
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

    def __init__(self, time, prop_nr, precision=11, timezone=0, calendarmodel=None,
                 concept_base_uri=None, is_reference=False, is_qualifier=False, snak_type='value',
                 references=None, qualifiers=None, rank='normal', check_qualifier_equality=True):
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
        :param calendarmodel: The calendar model used for the date. URL to the WD calendar model item or the QID.
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

        calendarmodel = config['CALENDAR_MODEL_QID'] if calendarmodel is None else calendarmodel
        concept_base_uri = config['CONCEPT_BASE_URI'] if concept_base_uri is None else concept_base_uri

        if calendarmodel.startswith('Q'):
            calendarmodel = concept_base_uri + calendarmodel

        # the value is composed of what is requried to define the WD time object
        value = (time, timezone, precision, calendarmodel)

        super(WDTime, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                                     is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank,
                                     prop_nr=prop_nr, check_qualifier_equality=check_qualifier_equality)

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
            assert isinstance(self.time, str), \
                "WDTime time must be a string in the following format: '+%Y-%m-%dT%H:%M:%SZ'"
            if self.precision < 0 or self.precision > 14:
                raise ValueError('Invalid value for time precision, '
                                 'see https://www.mediawiki.org/wiki/Wikibase/DataModel/JSON#time')
            if not (self.time.startswith("+") or self.time.startswith("-")):
                self.time = "+" + self.time

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

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
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
                                    is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank,
                                    prop_nr=prop_nr, check_qualifier_equality=check_qualifier_equality)

        self.set_value(value)

    def set_value(self, value):
        if value is None:
            self.value = None
        else:
            protocols = ['http://', 'https://', 'ftp://', 'irc://', 'mailto:']
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

    def __init__(self, value, prop_nr, language='en', is_reference=False, is_qualifier=False, snak_type='value',
                 references=None, qualifiers=None, rank='normal', check_qualifier_equality=True):
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

        super(WDMonolingualText, self) \
            .__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                      is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank,
                      prop_nr=prop_nr, check_qualifier_equality=check_qualifier_equality)

        self.set_value(value)

    def set_value(self, value):
        value = value[0]
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        self.json_representation['datavalue'] = {
            'value': {
                'text': value,
                'language': self.language
            },
            'type': 'monolingualtext'
        }

        super(WDMonolingualText, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])

        value = jsn['datavalue']['value']
        return cls(value=value['text'], prop_nr=jsn['property'], language=value['language'])


class WDQuantity(WDBaseDataType):
    """
    Implements the Wikidata data type for quantities
    """
    DTYPE = 'quantity'

    def __init__(self, value, prop_nr, upper_bound=None, lower_bound=None, unit='1', is_reference=False,
                 is_qualifier=False, snak_type='value', references=None, qualifiers=None, rank='normal',
                 check_qualifier_equality=True, concept_base_uri=None):
        """
        Constructor, calls the superclass WDBaseDataType

        :param value: The quantity value
        :type value: float, str
        :param prop_nr: The WD item ID for this claim
        :type prop_nr: str with a 'P' prefix followed by digits
        :param upper_bound: Upper bound of the value if it exists, e.g. for standard deviations
        :type upper_bound: float, str
        :param lower_bound: Lower bound of the value if it exists, e.g. for standard deviations
        :type lower_bound: float, str
        :param unit: The WD unit item URL or the QID a certain quantity has been measured
                        in (https://www.wikidata.org/wiki/Wikidata:Units). The default is dimensionless, represented by
                        a '1'
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

        concept_base_uri = config['CONCEPT_BASE_URI'] if concept_base_uri is None else concept_base_uri

        if unit.startswith('Q'):
            unit = concept_base_uri + unit

        v = (value, unit, upper_bound, lower_bound)

        super(WDQuantity, self).__init__(value=v, snak_type=snak_type, data_type=self.DTYPE,
                                         is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                         qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                         check_qualifier_equality=check_qualifier_equality)

        self.set_value(v)

    def set_value(self, v):
        value, unit, upper_bound, lower_bound = v

        if value is not None:
            value = self.format_amount(value)
            unit = str(unit)
            if upper_bound:
                upper_bound = self.format_amount(upper_bound)
            if lower_bound:
                lower_bound = self.format_amount(lower_bound)

            # Integrity checks for value and bounds
            try:
                for i in [value, upper_bound, lower_bound]:
                    if i:
                        float(i)
            except ValueError as e:
                raise ValueError('Value, bounds and units must parse as integers or float')

            if (lower_bound and upper_bound) and (float(lower_bound) > float(upper_bound)
                                                  or float(lower_bound) > float(value)):
                raise ValueError('Lower bound too large')

            if upper_bound and float(upper_bound) < float(value):
                raise ValueError('Upper bound too small')

        self.json_representation['datavalue'] = {
            'value': {
                'amount': value,
                'unit': unit,
                'upperBound': upper_bound,
                'lowerBound': lower_bound
            },
            'type': 'quantity'
        }

        # remove bounds from json if they are undefined
        if not upper_bound:
            del self.json_representation['datavalue']['value']['upperBound']

        if not lower_bound:
            del self.json_representation['datavalue']['value']['lowerBound']

        self.value = (value, unit, upper_bound, lower_bound)
        super(WDQuantity, self).set_value(value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, upper_bound=None, lower_bound=None, prop_nr=jsn['property'],
                       snak_type=jsn['snaktype'])

        value = jsn['datavalue']['value']
        upper_bound = value['upperBound'] if 'upperBound' in value else None
        lower_bound = value['lowerBound'] if 'lowerBound' in value else None
        return cls(value=value['amount'], prop_nr=jsn['property'], upper_bound=upper_bound,
                   lower_bound=lower_bound, unit=value['unit'])

    def format_amount(self, amount):
        # Remove .0 by casting to int
        if float(amount) % 1 == 0:
            amount = int(float(amount))

        # Adding prefix + for positive number and 0
        if not str(amount).startswith('+') and float(amount) >= 0:
            amount = str('+{}'.format(amount))

        # return as string
        return str(amount)


class WDCommonsMedia(WDBaseDataType):
    """
    Implements the Wikidata data type for Wikimedia commons media files
    """
    DTYPE = 'commonsMedia'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
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

        super(WDCommonsMedia, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                             is_reference=is_reference, is_qualifier=is_qualifier,
                                             references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                             check_qualifier_equality=check_qualifier_equality)

        self.set_value(value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
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

class WDLocalMedia(WDBaseDataType):
    """
    Implements the data type for Wikibase local media files.
    The new data type is introduced via the LocalMedia extension
    https://github.com/ProfessionalWiki/WikibaseLocalMedia
    """
    DTYPE = 'localMedia'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
        """
        Constructor, calls the superclass WDBaseDataType

        :param value: The media file name from the local Mediawiki to be used as the value
        :type value: str
        :param prop_nr: The property id for this claim
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

        super(WDLocalMedia, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                           is_reference=is_reference, is_qualifier=is_qualifier,
                                           references=references, qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                           check_qualifier_equality=check_qualifier_equality)

        self.set_value(value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        self.json_representation['datavalue'] = {
            'value': value,
            'type': 'string'
        }

        super(WDLocalMedia, self).set_value(value)

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

    def __init__(self, latitude, longitude, precision, prop_nr, globe=None,
                 concept_base_uri=None, is_reference=False, is_qualifier=False,
                 snak_type='value', references=None, qualifiers=None, rank='normal', check_qualifier_equality=True):
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

        globe = config['COORDINATE_GLOBE_QID'] if globe is None else globe
        concept_base_uri = config['CONCEPT_BASE_URI'] if concept_base_uri is None else concept_base_uri

        if globe.startswith('Q'):
            globe = concept_base_uri + globe

        value = (latitude, longitude, precision, globe)

        super(WDGlobeCoordinate, self) \
            .__init__(value=value, snak_type=snak_type, data_type=self.DTYPE, is_reference=is_reference,
                      is_qualifier=is_qualifier, references=references, qualifiers=qualifiers, rank=rank,
                      prop_nr=prop_nr, check_qualifier_equality=check_qualifier_equality)

        self.set_value(value)

    def set_value(self, value):
        # TODO: Introduce validity checks for coordinates

        self.latitude, self.longitude, self.precision, self.globe = value

        self.json_representation['datavalue'] = {
            'value': {
                'latitude': self.latitude,
                'longitude': self.longitude,
                'precision': self.precision,
                'globe': self.globe
            },
            'type': 'globecoordinate'
        }

        super(WDGlobeCoordinate, self).set_value(self.latitude)

        self.value = value

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(latitude=None, longitude=None, precision=None, prop_nr=jsn['property'],
                       snak_type=jsn['snaktype'])

        value = jsn['datavalue']['value']
        return cls(latitude=value['latitude'], longitude=value['longitude'], precision=value['precision'],
                   prop_nr=jsn['property'])


class WDGeoShape(WDBaseDataType):
    """
    Implements the Wikidata data type 'geo-shape'
    """
    DTYPE = 'geo-shape'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
        """
        Constructor, calls the superclass WDBaseDataType

        :param value: The GeoShape map file name in Wikimedia Commons to be linked
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

        super(WDGeoShape, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                         is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                         qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                         check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        pattern = re.compile('Data:((?![:|#]).)+\.map')
        matches = pattern.match(value)

        if not matches:
            raise ValueError(
                'Value must start with Data: and end with .map. In addition title should not contain characters like colon, hash or pipe.')

        self.value = value

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

        super(WDGeoShape, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])


class WDMusicalNotation(WDBaseDataType):
    """
    Implements the Wikidata data type 'string'
    """
    DTYPE = 'musical-notation'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
        """
        Constructor, calls the superclass WDBaseDataType

        :param value: Values for that data type are strings describing music following LilyPond syntax.
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

        super(WDMusicalNotation, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                                is_reference=is_reference, is_qualifier=is_qualifier,
                                                references=references,
                                                qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                                check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        self.value = value

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

        super(WDMusicalNotation, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])


class WDTabularData(WDBaseDataType):
    """
    Implements the Wikidata data type 'tabular-data'
    """
    DTYPE = 'tabular-data'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
        """
        Constructor, calls the superclass WDBaseDataType

        :param value: Reference to tabular data file on Wikimedia Commons.
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

        super(WDTabularData, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                            is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                            qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                            check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        pattern = re.compile('Data:((?![:|#]).)+\.tab')
        matches = pattern.match(value)

        if not matches:
            raise ValueError(
                'Value must start with Data: and end with .tab. In addition title should not contain characters like colon, hash or pipe.')

        self.value = value

        self.json_representation['datavalue'] = {
            'value': self.value,
            'type': 'string'
        }

        super(WDTabularData, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value'], prop_nr=jsn['property'])


class WDLexeme(WDBaseDataType):
    """
    Implements the Wikidata data type with value 'wikibase-lexeme'
    """
    DTYPE = 'wikibase-lexeme'
    sparql_query = '''
        PREFIX wd: <{wb_url}/entity/>
        PREFIX wdt: <{wb_url}/prop/direct/>
        PREFIX p: <{wb_url}/prop/>
        PREFIX ps: <{wb_url}/prop/statement/>
        PREFIX pq: <{wb_url}/prop/qualifier/>
        SELECT * WHERE {{
          ?item_id p:{pid} ?s .
          ?s ps:{pid} wd:L{value} .
          OPTIONAL {{?s pq:{mrt_pid} ?mrt}}
        }}
    '''

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):

        """
        Constructor, calls the superclass WDBaseDataType

        :param value: The WD lexeme number to serve as a value
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

        super(WDLexeme, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                       is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                       qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                       check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, (str, int)) or value is None, \
            "Expected str or int, found {} ({})".format(type(value), value)
        if value is None:
            self.value = value
        elif isinstance(value, int):
            self.value = value
        elif value.startswith("L"):
            pattern = re.compile('[0-9]+')
            matches = pattern.match(value[1:])

            if len(value[1:]) == len(matches.group(0)):
                self.value = int(value[1:])
            else:
                raise ValueError('Invalid WD lexeme ID, format must be "L[0-9]*"')
        else:
            raise ValueError('Invalid WD lexeme ID, format must be "L[0-9]*"')

        self.json_representation['datavalue'] = {
            'value': {
                'entity-type': 'lexeme',
                'numeric-id': self.value,
                'id': 'L{}'.format(self.value)
            },
            'type': 'wikibase-entityid'
        }

        super(WDLexeme, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value']['numeric-id'], prop_nr=jsn['property'])


class WDForm(WDBaseDataType):
    """
    Implements the Wikidata data type with value 'wikibase-form'
    """
    DTYPE = 'wikibase-form'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):
        """
        Constructor, calls the superclass WDBaseDataType

        :param value: The WD form number to serve as a value using the format "L<Lexeme ID>-F<Form ID>" (example: L252248-F2)
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

        super(WDForm, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                     is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                     qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                     check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        if value is None:
            self.value = value
        elif value.startswith("L"):
            pattern = re.compile('^L[0-9]+-F[0-9]+$')
            matches = pattern.match(value)

            if not matches:
                raise ValueError('Invalid WD form ID, format must be "L[0-9]+-F[0-9]+"')
        else:
            raise ValueError('Invalid WD form ID, format must be "L[0-9]+-F[0-9]+"')

        self.json_representation['datavalue'] = {
            'value': {
                'entity-type': 'form',
                'id': self.value
            },
            'type': 'wikibase-entityid'
        }

        super(WDForm, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value']['id'], prop_nr=jsn['property'])


class WDSense(WDBaseDataType):
    """
    Implements the Wikidata data type with value 'wikibase-sense'
    """
    DTYPE = 'wikibase-sense'

    def __init__(self, value, prop_nr, is_reference=False, is_qualifier=False, snak_type='value', references=None,
                 qualifiers=None, rank='normal', check_qualifier_equality=True):

        """
        Constructor, calls the superclass WDBaseDataType

        :param value: The WD form number to serve as a value using the format "L<Lexeme ID>-F<Form ID>" (example: L252248-F2)
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

        super(WDSense, self).__init__(value=value, snak_type=snak_type, data_type=self.DTYPE,
                                      is_reference=is_reference, is_qualifier=is_qualifier, references=references,
                                      qualifiers=qualifiers, rank=rank, prop_nr=prop_nr,
                                      check_qualifier_equality=check_qualifier_equality)

        self.set_value(value=value)

    def set_value(self, value):
        assert isinstance(value, str) or value is None, "Expected str, found {} ({})".format(type(value), value)
        if value is None:
            self.value = value
        elif value.startswith("L"):
            pattern = re.compile('^L[0-9]+-S[0-9]+$')
            matches = pattern.match(value)

            if not matches:
                raise ValueError('Invalid WD sense ID, format must be "L[0-9]+-S[0-9]+"')
        else:
            raise ValueError('Invalid WD sense ID, format must be "L[0-9]+-S[0-9]+"')

        self.json_representation['datavalue'] = {
            'value': {
                'entity-type': 'sense',
                'id': self.value
            },
            'type': 'wikibase-entityid'
        }
        super(WDSense, self).set_value(value=value)

    @classmethod
    @JsonParser
    def from_json(cls, jsn):
        if jsn['snaktype'] == 'novalue' or jsn['snaktype'] == 'somevalue':
            return cls(value=None, prop_nr=jsn['property'], snak_type=jsn['snaktype'])
        return cls(value=jsn['datavalue']['value']['id'], prop_nr=jsn['property'])


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
        This class handles errors returned from the WD API due to an attempt to create an item which has the same \
        label and description as an existing item in a certain language.\

        :param wd_error_message: An WD API error mesage containing 'wikibase-validator-label-with-description-conflict'\
         as the message name.\
        :type wd_error_message: A Python json representation dictionary of the error message\

        :return:"""

        self.wd_error_msg = wd_error_message

    def get_language(self):
        """
        :return: Returns a 2 letter Wikidata language string, indicating the language which triggered the error
        """
        return self.wd_error_msg['error']['messages'][0]['parameters'][1]

    def get_conflicting_item_qid(self):
        """
        TODO: Needs better explanation

        :return: Returns the QID string of the item which has the same label and description as the one which should
            be set.
        """
        qid_string = self.wd_error_msg['error']['messages'][0]['parameters'][2]

        return qid_string.split('|')[0][2:]

    def __str__(self):
        return repr(self.wd_error_msg)


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


class CorePropIntegrityException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MergeError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class FormatterWithHeader(logging.Formatter):
    def __init__(self, header, **kwargs):
        super(FormatterWithHeader, self).__init__(**kwargs)
        self.header = header
        self.format = self.first_line_format

    def first_line_format(self, record):
        # First time in, switch back to the normal format function
        self.format = super(FormatterWithHeader, self).format
        return self.header + "\n" + self.format(record)

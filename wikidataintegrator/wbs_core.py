from ShExJSG import ShExJ, ShExC
from pyshex.utils.schema_loader import SchemaLoader
from wikidataintegrator import wdi_core, wdi_login
import pprint
import json
import requests
import pdb

"""
Authors:
  Andra Waagmeester (andra' at ' micelio.be)

This file is part of the WikidataIntegrator.

"""
__author__ = 'Andra Waagmeester'
__license__ = 'MIT'

class WikibaseEngine(object):

    def __init__(self, wikibase_url=''):
        """
        constructor
        :param wikibase_url: The base url of the wikibase being accessed (e.g. for wikidata https://www.wikidata.org
        """
        self.wikibase_url = wikibase_url
        self.wikibase_api = wikibase_url + "/w/api.php"

    @classmethod
    def extractProperties(cls, d, properties):
        for k, v in d.items():
            if isinstance(v, dict):
                cls.extractProperties(v, properties)
            elif isinstance(v, list):
                for vl in v:
                    if isinstance(vl, dict):
                        cls.extractProperties(vl, properties)
            else:
                if k == "predicate" and v != "label" and v != "description":
                    properties.append(v)

    def createProperty(self, login, labels, descriptions, property_datatype, languages=["en", "nl"]):
        #pdb.set_trace()
        s = []
        item = wdi_core.WDItemEngine(new_item=True, mediawiki_api_url=self.wikibase_api)
        for language in labels.keys():
            if labels[language]["value"] in self.listProperties():
                return labels[language]["value"] + " already exists"
            if language in languages:
                item.set_label(labels[language]["value"], lang=language)
                if language in descriptions.keys():
                    item.set_description(descriptions[language]["value"], lang=language)
        return item.write(login, entity_type="property", property_datatype=property_datatype)

    def getNamespace(self, nsName):
        namespaces = json.loads(
            requests.get(self.wikibase_api + "?action=query&format=json&meta=siteinfo&formatversion=2&siprop=namespaces").text)
        for namespace in namespaces["query"]["namespaces"].keys():
            if namespaces["query"]["namespaces"][namespace]["name"] == nsName:
                return namespace

    def listProperties(self):
        propertyLabels = []
        ns = self.getNamespace("Property")
        query_url = self._build_list_properties_query(ns)
        properties = json.loads(requests.get(query_url).text)
        if 'query' not in properties:
            # wikibase is empty
            return []

        self._extract_labels_from_properties(properties, propertyLabels)
        while 'continue' in properties:
            gapcontinue = properties['continue']['gapcontinue']
            query_url = self._build_list_properties_query(ns, gapcontinue)
            properties = json.loads(requests.get(query_url).text)
            self._extract_labels_from_properties(properties, propertyLabels)

        return propertyLabels

    def copyProperties(self, login, wikibase_source, source_schema):
        loader = SchemaLoader()
        shex = requests.get(source_schema).text
        schema = loader.loads(shex)
        model = json.loads(schema._as_json_dumps())
        properties = []
        self.extractProperties(model, properties)
        props = list(set(properties))
        for prop in props:
            p = prop.split("/")
            if p[len(p) - 1].startswith("P"):
                print(p[len(p) - 1])
                page = json.loads(requests.get(
                    wikibase_source+"/w/api.php?action=wbgetentities&format=json&ids=" + p[len(p) - 1]).text)
                print(self.createProperty(login, page['entities'][p[len(p) - 1]]["labels"],
                                          page['entities'][p[len(p) - 1]]["descriptions"],
                                          page['entities'][p[len(p) - 1]]["datatype"]))

    def _build_list_properties_query(self, ns, gapcontinue=None):
        res = [self.wikibase_api,
               "?action=query&format=json&prop=pageterms&generator=allpages&wbptterms" \
               "=label&gapnamespace=",
               ns]
        if gapcontinue is not None:
            res.append("&gapcontinue=")
            res.append(gapcontinue)
        return ''.join(res)

    def _extract_labels_from_properties(self, properties, propertyLabels):
        for prop in properties["query"]["pages"].values():
            for label in prop["terms"]["label"]:
                propertyLabels.append(label)

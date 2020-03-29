from pyshex.utils.schema_loader import SchemaLoader
from wikidataintegrator import wdi_core
import json
import requests

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
        s = []
        item = wdi_core.WDItemEngine(new_item=True, mediawiki_api_url=self.wikibase_api)
        props = self.listProperties()
        for language, label in labels.items():
            if label["value"] in props:
                return label["value"] + " already exists"
            if language in languages:
                item.set_label(label["value"], lang=language)
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
        """
        List the properties of the target wikibase instance.

        :returns: List of labels of each property in the wikibase.
        :rtype: List[str]
        """
        property_labels = []
        ns = self.getNamespace("Property")
        query_url = self._build_list_properties_query(ns)
        properties = json.loads(requests.get(query_url).text)
        if 'query' not in properties:
            # wikibase is empty
            return []

        self._extract_labels_from_properties(properties, property_labels)
        while 'continue' in properties:
            gapcontinue = properties['continue']['gapcontinue']
            query_url = self._build_list_properties_query(ns, gapcontinue)
            properties = json.loads(requests.get(query_url).text)
            self._extract_labels_from_properties(properties, property_labels)

        return property_labels

    def copyProperties(self, login, wikibase_source, source_schema, languages=["en", "nl"]):
        """
        Copy the properties from a wikibase instance to another using a ShEx schema.

        :param login: An object of type WDLogin, which holds the credentials of the target wikibase instance.
        :type login: wdi_login.WDLogin
        :param wikibase_source: Base URL pointing to the source wikibase instance where the properties are stored.
        :type wikibase_source: str
        :param source_schema: URL pointing to an entity schema from which the properties
            will be obtained (e.g. https://www.wikidata.org/wiki/Special:EntitySchemaText/E37).
        :type source_schema: str
        :param languages: List of languages the labels and descriptions of the properties in the target wikibase.
        :type languages: List[str]
        """
        loader = SchemaLoader()
        shex = requests.get(source_schema).text
        schema = loader.loads(shex)
        model = json.loads(schema._as_json_dumps())
        properties = []
        self.extractProperties(model, properties)
        props = list(set(properties))
        for prop in props:
            p = prop.split("/")
            if p[-1].startswith("P"):
                prop_id = p[-1]
                print(prop_id)
                page = json.loads(requests.get(
                    wikibase_source+"/w/api.php?action=wbgetentities&format=json&ids=" + prop_id).text)
                print(self.createProperty(login, page['entities'][prop_id]['labels'],
                                          page['entities'][prop_id]['descriptions'],
                                          page['entities'][prop_id]['datatype'],
                                          languages))

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

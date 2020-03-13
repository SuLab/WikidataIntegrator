from ShExJSG import ShExJ, ShExC
from pyshex.utils.schema_loader import SchemaLoader
from wikidataintegrator import wdi_core, wdi_login
import pprint
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
    def __init__(self, wikibase_url='http://www.wikidata.org', wikibase_sparql="https://query.wikidata.org/sparql"):
        self.wikibase_url = wikibase_url
        self.wikibase_sparql = wikibase_sparql
        self.wikibase_api = wikibase_url+"/w/api.php"

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
        for language in labels.keys():

            if labels[language]["value"] in listProperties(self.wikibase_api):
                return labels[language]["value"] + " allready exists"
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
        properties = json.loads(requests.get(
            self.wikibase_api + "?action=query&format=json&prop=pageterms&generator=allpages&wbptterms=label&gapnamespace=" + ns).text)
        for property in properties["query"]["pages"].keys():
            for label in properties["query"]["pages"][property]["terms"]["label"]:
                propertyLabels.append(label)
        return propertyLabels

    def copyProperties(self,  wikibase_source, wikibase_target, schema="https://www.wikidata.org/wiki/Special:EntitySchemaText/E37"):
        if "TARGETUSER" in os.environ and "TARGETPASS" in os.environ:
            TARGETUSER = os.environ['TARGETUSER']
            TARGETPASS = os.environ['TARGETPASS']
        else:
            raise ValueError("TARGETUSER and TARGETPASS must be specified in local.py or as environment variables")

        self.targetlogin = wdi_login.WDLogin(TARGETUSER, TARGETPASS)

        loader = SchemaLoader()
        shex = requests.get(schema).text
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
                    "https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids=" + p[len(p) - 1]).text)
                print(self.createProperty(self.targetlogin, page['entities'][p[len(p) - 1]]["labels"],
                                     page['entities'][p[len(p) - 1]]["descriptions"],
                                     page['entities'][p[len(p) - 1]]["datatype"]))



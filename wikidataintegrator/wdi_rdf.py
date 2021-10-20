from rdflib import Graph, URIRef, Literal, Namespace, BNode
from rdflib.namespace import RDF, RDFS, SKOS, XSD, OWL, PROV
from wikidataintegrator import wdi_core, wdi_config
import uuid
import requests
import json
import urllib.parse

"""
Authors:
Andra Waagmeester (andra' at ' micelio.be)

This file is part of the WikidataIntegrator.
"""

__author__ = 'Andra Waagmeester'
__license__ = 'MIT'


class WDqidRDFEngine(object):
    def __init__(self, qid=None, json_data=None, fetch_provenance_rdf=True, fetch_metadata_rdf=True, fetch_truthy_rdf=False,
                 fetch_normalized_rdf=False, fetch_sitelinks_rdf=False,
                 fetch_merged_items_rdf=False, fetch_property_descriptions_rdf=False, fetch_labels_rdf=True,
                 fetch_linked_items_rdf=False, fetch_all=False, max_steps=1, current_step=0):
        self.current_step = current_step
        self.max_steps = max_steps
        if not bool(qid) and not bool(json_data):
            raise ValueError('Please provide a QID or a QID and its json object of a Wikidata item')

        if not bool(qid):
            raise ValueError('Please provide only the QID, even if the json object is provided')

        self.qid = qid
        if fetch_all:
            self.fetch_provenance_rdf = True
            self.fetch_labels_rdf = True
            self.fetch_metadata_rdf = True
            self.fetch_merged_items_rdf = True
            self.fetch_normalized_rdf = True
            self.fetch_property_descriptions_rdf = True
            self.fetch_sitelinks_rdf = True
            self.fetch_truthy_rdf = True
            self.fetch_linked_items_rdf = True
        else:
            self.fetch_provenance_rdf = fetch_provenance_rdf
            self.fetch_labels_rdf = fetch_labels_rdf
            self.fetch_metadata_rdf = fetch_metadata_rdf
            self.fetch_merged_items_rdf = fetch_merged_items_rdf
            self.fetch_normalized_rdf = fetch_normalized_rdf
            self.fetch_property_descriptions_rdf = fetch_property_descriptions_rdf
            self.fetch_sitelinks_rdf = fetch_sitelinks_rdf
            self.fetch_truthy_rdf = fetch_truthy_rdf
            self.fetch_linked_items_rdf = fetch_linked_items_rdf
        if bool(qid):
            self.json_item = json.loads(requests.get("http://www.wikidata.org/entity/" + qid + ".json").text)["entities"][
                qid]
        else:
            self.json_item = json_data
        self.rdf_item = Graph()
        self.ns = dict()
        self.linked_items = []
        self.metadata = {"identifiers": 0, "sitelinks": 0, "statements": 0}
        self.ns = dict()
        for prefix in wdi_config.prefix.keys():
            self.ns[prefix] = Namespace(wdi_config.prefix[prefix])
            self.rdf_item.namespace_manager.bind(prefix, self.ns[prefix])
        self.ns['schema'] = Namespace('http://schema.org/')  # can be removed since it will be in WDI version 0.8.21
        self.properties = dict()
        self.triplify()

    def triplify(self):
        self.fetch_normalization_rules()
        uriformat = self.normalization_rules["iri"]
        # qid = "Q35869"
        for prefix in wdi_config.prefix.keys():
            self.ns[prefix] = Namespace(wdi_config.prefix[prefix])
            self.rdf_item.namespace_manager.bind(prefix, self.ns[prefix])
        self.ns['schema'] = Namespace('http://schema.org/')  # can be removed since it will be in WDI version 0.8.21

        # item = wdi_core.WDItemEngine(wd_item_id=qid)

        self.fetch_statements()
        if self.fetch_metadata_rdf:
            self.fetch_metadata()
        if self.fetch_sitelinks_rdf:
            self.fetch_sitelinks()
        if self.fetch_merged_items_rdf:
            self.fetch_merged_items()
        if self.fetch_property_descriptions_rdf:
            for pid in self.properties.keys():
                pid_item = wdi_core.WDItemEngine(wd_item_id=pid).get_wd_json_representation()
                if self.fetch_labels_rdf:
                    self.fetch_labels(pid, pid_item)
                self.fetch_property_descriptions(pid, self.properties[pid])
        if self.fetch_linked_items_rdf:
            self.fetch_linked_items()

        self.turtle = self.rdf_item.serialize(format="turtle")

    def parseSnak(self, statement):
        if "datavalue" not in statement.keys():
            return BNode()
        value = statement["datavalue"]["value"]
        if statement["datatype"] == "commonsMedia":
            return URIRef("http://commons.wikimedia.org/wiki/Special:FilePath/" + urllib.parse.quote_plus(value.replace(" ", "_")))
        elif statement["datatype"] == "string":
            return Literal(value)
        elif statement["datatype"] == "external-id":
            return Literal(value)
        elif statement["datatype"] == "wikibase-item" or statement["datatype"] == "wikibase-property":
            if value["id"] not in self.linked_items:
                self.linked_items.append(value["id"])

            return self.ns["wd"][value["id"]]
        elif statement["datatype"] == "monolingualtext":
            return Literal(value["text"], value["language"])
        elif statement["datatype"] == "geo-shape":
            return URIRef("http://commons.wikimedia.org/data/main/" + value)
        elif statement["datatype"] == "globe-coordinate":
            latitude = value["latitude"]
            longitude = value["longitude"]
            # altitude = claim["mainsnak"]["datavalue"]["value"]["altitude"] # not used
            precision = value["precision"]  # not used
            globe = value["globe"]  # not used
            return Literal("Point(" + str(longitude) + "," + str(latitude) + ")", datatype=self.ns["geo"].wktLiteral)
        elif statement["datatype"] == "quantity":
            amount = value["amount"]
            unit = value["unit"]
            return Literal(value["amount"], datatype=XSD.decimal)
        elif statement["datatype"] == "time":
            return Literal(value["time"].replace("+", "").replace("Z", "+00:00"), datatype=XSD.dateTime)
        elif statement["datatype"] == "url":
            return URIRef(value)
        else:
            raise ValueError('unknown snak datatype ' + statement["datatype"])

    def fetch_labels(self, qid, json_item):
        # Heading
        for language in json_item["labels"].keys():
            self.rdf_item.add(
                (self.ns["wd"][qid], RDFS.label, Literal(json_item["labels"][language]["value"], language)))
            self.rdf_item.add(
                (self.ns["wd"][qid], self.ns["schema"].name, Literal(json_item["labels"][language]["value"], language)))
            self.rdf_item.add((self.ns["wd"][qid], self.ns["skos"].prefLabel,
                               Literal(json_item["labels"][language]["value"], language)))

        for language in json_item["descriptions"].keys():
            self.rdf_item.add((self.ns["wd"][qid], self.ns["schema"].description,
                               Literal(json_item["descriptions"][language]["value"], language)))

        for language in json_item["aliases"].keys():
            for label in json_item["aliases"][language]:
                self.rdf_item.add((self.ns["wd"][qid], SKOS.altLabel, Literal(label["value"], language)))

    def fetch_linked_items(self):
        for linked_qid in self.linked_items:
            self.rdf_item.add((self.ns["wd"][linked_qid], RDF.type, self.ns["wikibase"].Item))
            linked_qid_item = wdi_core.WDItemEngine(wd_item_id=linked_qid).get_wd_json_representation()
            if self.current_step < self.max_steps:
                self.rdf_item = self.rdf_item + WDqidRDFEngine(qid=linked_qid,json_data=linked_qid_item,max_steps=self.max_steps, current_step=self.current_step+1).rdf_item
            self.fetch_labels(linked_qid, linked_qid_item)

    def fetch_metadata(self):
        self.metadata["statements"] += self.metadata["identifiers"]
        self.rdf_item.add((self.ns["data"][self.qid], RDF.type, self.ns["schema"].Dataset))
        self.rdf_item.add((self.ns["data"][self.qid], self.ns["cc"].license,
                           URIRef("http://creativecommons.org/publicdomain/zero/1.0/")))
        self.rdf_item.add((self.ns["data"][self.qid], self.ns["schema"].about, self.ns["wd"][self.qid]))
        self.rdf_item.add((self.ns["data"][self.qid], self.ns["schema"].softwareVersion, Literal("1.0.0")))
        self.rdf_item.add(
            (self.ns["data"][self.qid], self.ns["wikibase"].identifiers, Literal(self.metadata["identifiers"])))
        self.rdf_item.add(
            (self.ns["data"][self.qid], self.ns["wikibase"].sitelinks, Literal(self.metadata["sitelinks"])))
        self.rdf_item.add(
            (self.ns["data"][self.qid], self.ns["wikibase"].statements, Literal(self.metadata["statements"])))
        self.rdf_item.add((self.ns["data"][self.qid], self.ns["schema"].version, Literal(self.json_item["lastrevid"])))
        self.rdf_item.add((self.ns["data"][self.qid], self.ns["schema"].dateModified,
                           Literal(self.json_item["modified"].replace("Z", "+00:00"), datatype=XSD.dateTime)))

    def fetch_merged_items(self):
        # Merged items
        merged_items = json.loads(requests.get(
            "https://www.wikidata.org/w/api.php?action=query&prop=redirects&format=json&titles=" + self.qid).text)
        for page in merged_items["query"]["pages"].keys():
            if "redirects" in merged_items["query"]["pages"][page].keys():
                for redirect in merged_items["query"]["pages"][page]["redirects"]:
                    self.rdf_item.add((self.ns["wd"][redirect["title"]], OWL.sameAs, self.ns["wd"][self.qid]))

    def fetch_normalization_rules(self):
        self.normalization_rules = {"iri": {}}
        query = """
           SELECT DISTINCT ?prop ?format WHERE {
           ?prop wdt:P1921 ?format .
        }
        """
        df = wdi_core.WDFunctionsEngine.execute_sparql_query(query, as_dataframe=True)
        for index, row in df.iterrows():
            if row["prop"].replace("http://www.wikidata.org/entity/", "") not in self.normalization_rules["iri"].keys():
                self.normalization_rules["iri"][row["prop"].replace("http://www.wikidata.org/entity/", "")] = []
            self.normalization_rules["iri"][row["prop"].replace("http://www.wikidata.org/entity/", "")].append(
                row["format"])
        # SI conversion
        self.normalization_rules["siconversion"] = wdi_config.unit_conversion_rules

    def fetch_normalized_values(self, snakuri, snak, prop, value, snaktype):
        if snaktype == "qualifier":
            normprop = self.ns["pqv"]
        elif snaktype == "reference":
            normprop = self.ns["prv"]
        elif snaktype == "statement":
            normprop = self.ns["pv"]
        else:
            raise ValueError('unknown snak type (statement, qualifier, reference).')

        if snak["datatype"] == "time":
            uri = self.ns["v"][
                uuid.uuid4()]  # TODO: fix to wikidata hash once I figured out how the hashes are composed
            self.rdf_item.add((snakuri, normprop[prop], uri))
            self.rdf_item.add((uri, RDF.type, self.ns["wikibase"].TimeValue))
            self.rdf_item.add((uri, self.ns["wikibase"].timeValue, value))
            self.rdf_item.add(
                (uri, self.ns["wikibase"].timePrecision, Literal(snak["datavalue"]["value"]["precision"])))
            self.rdf_item.add((uri, self.ns["wikibase"].timeTimezone, Literal(snak["datavalue"]["value"]["timezone"])))
            self.rdf_item.add(
                (uri, self.ns["wikibase"].timeCalendarModel, URIRef(snak["datavalue"]["value"]["calendarmodel"])))
        if snak["datatype"] == "quantity":
            uri = self.ns["v"][
                uuid.uuid4()]  # TODO: fix to wikidata hash once I figured out how the hashes are composed
            if prop in self.normalization_rules["siconversion"].keys():
                if siconversion[prop]["factor"] == "1":
                    self.rdf_item.add((uri, self.ns["wikibase"].quantityNormalized, uri))
                else:
                    normalized_uri = self.ns["v"][
                        uuid.uuid4()]  # TODO: fix to wikidata hash once I figured out how the hashes are composed
                    self.rdf_item.add((normalized_uri, normprop[prop], normalized_uri))
                    self.rdf_item.add((normalized_uri, RDF.type, self.ns["wikibase"].QuantityValue))
                    self.rdf_item.add((normalized_uri, self.ns["wikibase"].quantityAmount,
                                       Literal(snak["datavalue"]["value"]["amount"] * siconversion[prop]["factor"])))
                    if snak["datavalue"]["value"]["unit"] == "1":
                        self.rdf_item.add((uri, self.ns["wikibase"].quantityUnit, self.ns["wd"].Q199))
                    else:
                        self.rdf_item.add(
                            (uri, self.ns["wikibase"].quantityUnit, self.ns["wd"][siconversion[prop]["unit"]]))

            self.rdf_item.add((snakuri, normprop[prop], uri))
            self.rdf_item.add((uri, RDF.type, self.ns["wikibase"].QuantityValue))
            self.rdf_item.add((uri, self.ns["wikibase"].quantityAmount, Literal(snak["datavalue"]["value"]["amount"])))
            if snak["datavalue"]["value"]["unit"] == "1":
                self.rdf_item.add((uri, self.ns["wikibase"].quantityUnit, self.ns["wd"].Q199))
            else:
                self.rdf_item.add((uri, self.ns["wikibase"].quantityUnit, URIRef(snak["datavalue"]["value"]["unit"])))
        if snak["datatype"] == "globe-coordinate":
            uri = self.ns["v"][
                uuid.uuid4()]  # TODO: fix to wikidata hash once I figured out how the hashes are composed
            self.rdf_item.add((snakuri, normprop[prop], uri))
            self.rdf_item.add((uri, RDF.type, self.ns["wikibase"].GlobecoordinateValue))
            self.rdf_item.add((uri, self.ns["wikibase"].geoLatitude, Literal(snak["datavalue"]["value"]["latitude"])))
            self.rdf_item.add((uri, self.ns["wikibase"].geoLongitude, Literal(snak["datavalue"]["value"]["longitude"])))
            self.rdf_item.add((uri, self.ns["wikibase"].geoGlobe, self.ns["wd"][snak["datavalue"]["value"]["globe"]]))

    def owlPropertyTypes(self, owlType, pid):
        self.rdf_item.add((self.ns["wd"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["p"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["wdtn"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["wdt"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["pq"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["pqn"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["pqv"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["pr"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["prn"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["prv"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["ps"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["psn"][pid], RDF.type, owlType))
        self.rdf_item.add((self.ns["psv"][pid], RDF.type, owlType))

    def fetch_property_descriptions(self, pid, datatype):
        ## Properties and their derivatives
        object_properties = ["wikibase-item", "wikibase-property", 'external-id', 'string', 'commonsMedia', 'time', 'edtf',
                             'globe-coordinate', 'url', 'quantity', 'wikibase-property', 'monolingualtext', 'math',
                             'tabular-data', 'form', 'lexeme', 'geo-shape', 'musical-notation', 'sense']
        data_properties = ['external-id', 'string', 'time', 'edtf', 'globe-coordinate', 'quantity', 'monolingualtext',
                           'math', 'geo-shape', 'form', 'lexeme', 'musical-notation', 'sense']
        # ObjectProperty
        if datatype in object_properties:
            self.owlPropertyTypes(OWL.ObjectProperty, pid)
        # Data Properties
        if datatype in data_properties:
            self.owlPropertyTypes(OWL.DatatypeProperty, pid)
        self.rdf_item.add((self.ns["wd"][pid], RDF.type, self.ns["wikibase"].Property))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].directClaim, self.ns["wdt"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].claim, self.ns["p"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].statementProperty, self.ns["ps"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].statementValue, self.ns["psv"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].qualifier, self.ns["pq"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].qualifierValue, self.ns["pqv"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].reference, self.ns["pr"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].referenceValue, self.ns["prv"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].novalue, self.ns["wdno"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].directClaimNormalized, self.ns["wdtn"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].qualifierValueNormalized, self.ns["pqn"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].referenceValueNormalized, self.ns["prn"][pid]))
        self.rdf_item.add((self.ns["wd"][pid], self.ns["wikibase"].statementValueNormalized, self.ns["psn"][pid]))
        self.rdf_item.add(
            (self.ns["wd"][pid], self.ns["wikibase"].propertyType, URIRef(wdi_config.property_value_types[datatype])))
        self.rdf_item.add((self.ns["wdno"][pid], RDF.type, OWL.Class))
        owl_restriction = BNode()
        self.rdf_item.add((owl_restriction, RDF.type, OWL.Restriction))
        self.rdf_item.add((owl_restriction, OWL.onProperty, self.ns["wdt"][pid]))
        self.rdf_item.add((owl_restriction, OWL.someValuesFrom, OWL.Thing))
        self.rdf_item.add((self.ns["wdno"][pid], OWL.complementOf, owl_restriction))

    def fetch_sitelinks(self):
        # sitelinks
        for sitelink in self.json_item['sitelinks'].keys():
            self.metadata["sitelinks"] += 1
            wiki = URIRef(self.json_item['sitelinks'][sitelink]["url"])
            # print(json_item['sitelinks'][sitelink]["url"])
            partof = URIRef(self.json_item['sitelinks'][sitelink]["url"].split("wiki/")[0])
            if "commons" in str(partof):
                group = str(partof).split(".")[0].replace("https://", "")
            else:
                group = str(partof).split(".")[1]
            self.rdf_item.add((partof, self.ns["wikibase"].wikiGroup, Literal(group)))
            if "quote" in sitelink:
                language = sitelink.replace("wikiquote", "")
            elif sitelink == "simplewiki":
                language = "en-simple"
            elif sitelink == "commonswiki":
                language = "en"
            elif sitelink == "zh_yuewiki":
                language = "yue"
            elif sitelink == "zh_min_nanwiki":
                language = "nan"
            elif sitelink == "nowiki":
                language = "nb"
            else:
                language = sitelink.replace("wiki", "")
            self.rdf_item.add((wiki, RDF.type, self.ns["schema"].Article))
            self.rdf_item.add((wiki, self.ns['schema'].about, self.ns["wd"][self.qid]))
            self.rdf_item.add((wiki, self.ns['schema'].isPartOf, URIRef(partof)))
            for badge in self.json_item['sitelinks'][sitelink]["badges"]:
                self.rdf_item.add((wiki, self.ns["wikibase"].badge, self.ns["wd"][badge]))
            try:
                self.rdf_item.add(
                    (wiki, self.ns['schema'].name, Literal(self.json_item['sitelinks'][sitelink]["title"], language)))
                self.rdf_item.add((wiki, self.ns['schema'].inLanguage, Literal(language)))
            except:
                print(language)

    def fetch_statements(self):
        uriformat = self.normalization_rules["iri"]
        self.rdf_item.add((self.ns["wd"][self.qid], RDF.type, self.ns["wikibase"].Item))
        for pid in self.json_item['claims'].keys():
            if pid not in self.properties.keys():
                self.properties[pid] = self.json_item['claims'][pid][0]["mainsnak"]["datatype"]
            ## Ststements
            for claim in self.json_item['claims'][pid]:
                if self.fetch_provenance_rdf:
                    statement_uri = self.ns["s"][claim["id"].replace("$", "-")]
                    # rank
                    if claim["rank"] == "normal":
                        self.rdf_item.add((statement_uri, self.ns["wikibase"].rank, self.ns["wikibase"].NormalRank))
                    if claim["rank"] == "preferred":
                        self.rdf_item.add((statement_uri, self.ns["wikibase"].rank, self.ns["wikibase"].PreferredRank))
                    if claim["rank"] == "deprecated":
                        self.rdf_item.add((statement_uri, self.ns["wikibase"].rank, self.ns["wikibase"].DeprecatedRank))

                    # values
                    for claim2 in self.json_item['claims'][pid]:
                        if claim2["rank"] == "preferred":
                            preferredSet = True
                            break
                    else:
                        preferredSet = False

                if claim["mainsnak"]["datatype"] == "external-id":
                    self.metadata["identifiers"] += 1
                else:
                    self.metadata["statements"] += 1

                if self.fetch_provenance_rdf:
                    if claim["mainsnak"]["snaktype"] == "novalue":
                        self.rdf_item.add((statement_uri, RDF.type, self.ns["wdno"][pid]))
                    else:
                        objectValue = self.parseSnak(claim["mainsnak"])
                        self.rdf_item.add((statement_uri, self.ns["ps"][pid], objectValue))
                        if pid in uriformat.keys():
                            for normProp in uriformat[pid]:
                                self.rdf_item.add(
                                    (statement_uri, self.ns["psn"][pid], URIRef(normProp.replace("$1", objectValue))))
                    self.rdf_item.add((self.ns["wd"][self.qid], self.ns["p"][pid], statement_uri))
                    self.rdf_item.add((statement_uri, RDF.type, self.ns["wikibase"].Statement))
                    if preferredSet:
                        if claim["rank"] == "preferred":
                            self.rdf_item.add((statement_uri, RDF.type, self.ns["wikibase"].BestRank))
                    else:
                        if claim["rank"] == "normal":
                            self.rdf_item.add((statement_uri, RDF.type, self.ns["wikibase"].BestRank))

                    # qualifiers
                    if "qualifiers" in claim.keys():
                        for qualifier in claim["qualifiers"].keys():
                            if qualifier not in self.properties.keys():
                                self.properties[qualifier] = claim["qualifiers"][qualifier][0]["datatype"]
                            for qualifier_prop in claim["qualifiers"][qualifier]:
                                if qualifier_prop["snaktype"] == "novalue":
                                    self.rdf_item.add((statement_uri, RDF.type, self.ns["wdno"][pid]))
                                else:
                                    object = self.parseSnak(qualifier_prop)
                                    self.rdf_item.add((statement_uri, self.ns["pq"][qualifier], object))
                                    if self.fetch_normalized_rdf:
                                        self.fetch_normalized_values(statement_uri, qualifier_prop, qualifier, object,
                                                                     "qualifier")

                    # references
                    if "references" in claim.keys():
                        for reference in claim["references"]:
                            reference_uri = self.ns["ref"][reference["hash"]]
                            self.rdf_item.add((reference_uri, RDF.type, self.ns["wikibase"].Reference))
                            self.rdf_item.add((statement_uri, PROV.wasDerivedFrom, reference_uri))

                            for ref_prop in reference["snaks"].keys():
                                if ref_prop not in self.properties.keys():
                                    self.properties[ref_prop] = reference["snaks"][ref_prop][0]["datatype"]
                                for ref_prop_statement in reference["snaks"][ref_prop]:
                                    object = self.parseSnak(ref_prop_statement)
                                    self.rdf_item.add((reference_uri, self.ns["pr"][ref_prop], object))
                                    if self.fetch_normalized_rdf:
                                        self.fetch_normalized_values(reference_uri, ref_prop_statement, ref_prop,
                                                                     object, "reference")

                if self.fetch_truthy_rdf:
                    if not claim["mainsnak"]["snaktype"] == "novalue":
                        if preferredSet:
                            if claim["rank"] == "preferred":
                                self.rdf_item.add((self.ns["wd"][self.qid], self.ns["wdt"][pid], objectValue))
                                if pid in uriformat.keys():
                                    for normProp in uriformat[pid]:
                                        self.rdf_item.add((self.ns["wd"][self.qid], self.ns["wdtn"][pid],
                                                           URIRef(normProp.replace("$1", objectValue))))
                        else:
                            if claim["rank"] == "normal":
                                self.rdf_item.add((self.ns["wd"][self.qid], self.ns["wdt"][pid], objectValue))
                                if pid in uriformat.keys():
                                    for normProp in uriformat[pid]:
                                        self.rdf_item.add((self.ns["wd"][self.qid], self.ns["wdtn"][pid],
                                                           URIRef(normProp.replace("$1", objectValue))))



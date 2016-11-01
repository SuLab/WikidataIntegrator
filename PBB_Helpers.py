import xml.etree.ElementTree as ET
from time import gmtime, strftime

import requests
from SPARQLWrapper import SPARQLWrapper, JSON

from . import PBB_Core, PBB_login
from .PBB_Core import WDItemEngine


class PubmedStub:
    """
    Get or create a wikidata item stub given a pubmed ID

    Usage:
    PubmedStub(22674334).create(login)

    """

    def __init__(self, pmid):
        self.pmid = str(pmid)
        self.title = None
        self.dois = None
        self.reference = None
        self.statements = None
        self._root = None
        self.wdid = SPARQLHelper().prop2qid('P698', self.pmid)  # if doesn't exist, will be None

    def _validate_pmid(self):
        pubmed_url = 'http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=Pubmed&Retmode=xml&id={}'.format(
            self.pmid)
        r = requests.get(pubmed_url)
        self._root = ET.fromstring(r.text)
        return True if self._root.find(".//MedlineCitation/Article/ArticleTitle") is not None else False

    def _parse_ncbi(self):
        self.title = self._root.find(".//MedlineCitation/Article/ArticleTitle").text
        doiset = self._root.findall(".//ArticleIdList/ArticleId[@IdType='doi']")
        self.dois = [x.text for x in doiset]

    def _make_reference(self):
        refStatedIn = PBB_Core.WDItemID(value='Q180686', prop_nr='P248', is_reference=True)
        refPubmedId = PBB_Core.WDString(value=self.pmid, prop_nr='P698', is_reference=True)
        timeStringNow = strftime("+%Y-%m-%dT00:00:00Z", gmtime())
        refRetrieved = PBB_Core.WDTime(timeStringNow, prop_nr='P813', is_reference=True)
        self.reference = [refStatedIn, refPubmedId, refRetrieved]

    def _make_statements(self):
        s = []
        # instance of scientific article
        s.append(PBB_Core.WDItemID('Q13442814', 'P31', references=[self.reference]))
        # pmid
        s.append(PBB_Core.WDExternalID(self.pmid, 'P698', references=[self.reference]))
        # title
        s.append(PBB_Core.WDMonolingualText(self.title, 'P1476', references=[self.reference]))
        for doi in self.dois:
            s.append(PBB_Core.WDExternalID(doi, 'P356', references=[self.reference]))
        self.statements = s

    def create(self, login):
        if self.wdid:
            return self.wdid
        if not self._validate_pmid():
            print("invalid pmid: {}".format(self.wdid))
            return None
        self._parse_ncbi()
        self._make_reference()
        self._make_statements()
        item = PBB_Core.WDItemEngine(item_name=self.title, data=self.statements, domain="scientific_article")
        item.set_label(self.title)
        item.set_description(description='scientific article', lang='en')
        try_write(item, self.pmid, 'P698', login)
        return item.wd_item_id


def try_write(wd_item, record_id, record_prop, login):
    """
    Write a PBB_core item. Log if item was created, updated, or skipped.
    Catch and log all errors.

    :param wd_item: A wikidata item that will be written
    :type wd_item: PBB_Core.WDItemEngine
    :param record_id: An external identifier, to be used for logging
    :type record_id: str
    :param record_prop: Property of the external identifier
    :type record_prop: str
    :param login: PBB_core login instance
    :type login: PBB_login.WDLogin
    :return: None
    """
    if wd_item.require_write:
        if wd_item.create_new_item:
            msg = "CREATE"
        else:
            msg = "UPDATE"
    else:
        msg = "SKIP"

    try:
        wd_item.write(login=login)
        PBB_Core.WDItemEngine.log("INFO", format_msg(record_id, msg, wd_item.wd_item_id, record_prop))
    except Exception as e:
        print(e)
        PBB_Core.WDItemEngine.log("ERROR", format_msg(record_id, str(e), wd_item.wd_item_id, record_prop))


def format_msg(main_data_id, message, wd_id, external_id_prop=None):
    """
    Format message for logging
    :return: str
    """
    # escape double quotes and quote string with commas,
    # so it can be read by pd.read_csv(fp, escapechar='\\')
    message = message.replace("\"", "\\\"")
    message = "\"" + message + "\"" if "," in message else message
    message = message.replace(",", "")
    msg = '{main_data_id},{message},{wd_id},{prop}'.format(
        main_data_id=main_data_id, message=message,
        wd_id=wd_id, prop=external_id_prop)
    return msg


def prop2qid(prop, value):
    """
    Lookup a wikidata item ID from a property and string value. For example, get the item QID for the
     item with the entrez gene id (P351): "899959"
    >>> prop2qid('P351','899959')
    :param prop: property
    :type prop: str
    :param value: value of property
    :type value: str
    :return: wdid as string or None
    """
    arguments = '?item wdt:{} "{}"'.format(prop, value)
    query = 'SELECT * WHERE {{{}}}'.format(arguments)
    results = WDItemEngine.execute_sparql_query(query)
    result = results['results']['bindings']
    if len(result) == 0:
        # not found
        return None
    elif len(result) > 1:
        raise ValueError("More than one wikidata ID found for {} {}: {}".format(prop, value, result))
    else:
        return result[0]['item']['value'].split("/")[-1]


def id_mapper(prop, filters=None):
    """
    Get all wikidata ID <-> prop <-> value mappings
    Example: id_mapper("P352") -> { 'A0KH68': 'Q23429083',
                                     'Q5ZWJ4': 'Q22334494',
                                     'Q53WF2': 'Q21766762', .... }
    Optional filters can filter query results.
    Example (get all uniprot to wdid, where taxon is human): id_mapper("P352",(("P703", "Q15978631"),))
    :param prop: wikidata property
    :type prop: str
    :param filters: list of tuples, where the first item is a property, second is a value
    :return: dict

    """
    query = "SELECT * WHERE {"
    query += "?item wdt:{} ?id .\n".format(prop)
    if filters:
        for f in filters:
            query += "?item wdt:{} wd:{} .\n".format(f[0], f[1])
    query = query + "}"
    results = WDItemEngine.execute_sparql_query(query)
    if not results['results']['bindings']:
        return None
    return {x['id']['value']: x['item']['value'].split('/')[-1] for x in results['results']['bindings']}

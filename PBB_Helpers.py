import datetime
import xml.etree.ElementTree as ET
from time import gmtime, strftime
import functools
import requests

from . import PBB_Core, PBB_login
from .PBB_Core import WDItemEngine


class Release(object):
    """
    Create a release item
    Example: Ensembl Release 86 Q27613766

    A relase item has the following required properties:
        title: **user_defined**
        description: **user_defined**
        instance of (P31): edition (Q3331189)
        edition or translation of (P629): **user_defined** (wd_item)
        edition number (P393): **user_defined** (str)
    Optional properties:
        archive URL (P1065): (str)
        publication date (P577): (wd_date)

    Example usage:
    r = PBB_Helpers.Release("Ensembl Release 85", "Release 85 of Ensembl", "85", edition_of="Ensembl",
                            archive_url="http://jul2016.archive.ensembl.org/",
                            pub_date='+2016-07-01T00:00:00Z', date_precision=10)
    r.create(login)

    """

    def __init__(self, title, description, edition, edition_of=None, edition_of_wdid=None, archive_url=None,
                 pub_date=None, date_precision=11):
        """

        :param title: title of release item
        :type title: str
        :param description: description of release item
        :type description: str
        :param edition: edition number or unique identifier for the release
        :type edition: str
        :param edition_of: name of database. database wdid will automatically be looked up. Must pass either edition_of or edition_of_wdid
        :type edition_of: str
        :param edition_of_wdid: wikidata id of database
        :type edition_of_wdid: str
        :param archive_url: (optional)
        :type archive_url: str
        :param pub_date: (optional) Datetime will be converted to str
        :type pub_date: str or datetime
        :param date_precision: (optional) passed to PBB_Core.WDTime as is. default is 11 (day)
        :type date_precision: int
        """
        self.title = title
        self.description = description
        self.edition = str(edition)
        self.archive_url = archive_url
        if isinstance(pub_date, datetime.date):
            self.pub_date = pub_date.strftime('+%Y-%m-%dT%H:%M:%SZ')
        else:
            self.pub_date = pub_date
        self.date_precision = date_precision

        if (edition_of is None and edition_of_wdid is None) or (edition_of and edition_of_wdid):
            raise ValueError("must provide either edition_of or edition_of_wdid")
        if edition_of:
            self.edition_of_wdid = self.lookup_database(edition_of)
        else:
            self.edition_of_wdid = edition_of_wdid

        self.statements = None
        self.make_statements()

    @staticmethod
    @functools.lru_cache()
    def lookup_database(edition_of):
        query = """SELECT ?item ?itemLabel WHERE {
                    ?item wdt:P31 wd:Q4117139 .
                    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
                }"""
        results = WDItemEngine.execute_sparql_query(query)
        db_item_map = {x['itemLabel']['value']: x['item']['value'].replace('http://www.wikidata.org/entity/', '') for x
                       in results['results']['bindings']}
        if edition_of not in db_item_map:
            raise ValueError("Database {} not found in wikidata. Please provide edition_of_wdid".format(edition_of))
        return db_item_map[edition_of]

    @functools.lru_cache()
    def release_exists(self):
        edition_dict = id_mapper("P393", (("P629", self.edition_of_wdid), ("P31", "Q3331189")))
        return edition_dict.get(self.edition, False)

    def make_statements(self):
        s = []
        # instance of edition
        s.append(PBB_Core.WDItemID('Q3331189', 'P31'))
        # edition or translation of
        s.append(PBB_Core.WDItemID(self.edition_of_wdid, 'P629'))
        # edition number
        s.append(PBB_Core.WDString(self.edition, 'P393'))

        if self.archive_url:
            s.append(PBB_Core.WDUrl(self.archive_url, 'P1065'))

        if self.pub_date:
            s.append(PBB_Core.WDTime(self.pub_date, 'P577', precision=self.date_precision))

        self.statements = s

    def get_or_create(self, login):
        re = self.release_exists()
        if re:
            return re
        item = PBB_Core.WDItemEngine(item_name=self.title, data=self.statements, domain="release")
        item.set_label(self.title)
        item.set_description(description=self.description, lang='en')
        try_write(item, self.edition + ";" + self.edition_of_wdid, 'P393;P629', login)
        return item.wd_item_id


class PubmedStub(object):
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
        self.wdid = prop2qid('P698', self.pmid)  # if doesn't exist, will be None

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


def try_write(wd_item, record_id, record_prop, login, edit_summary=''):
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
    :param edit_summary: passed directly to wd_item.write
    :type edit_summary: str
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
        wd_item.write(login=login, edit_summary=edit_summary)
        PBB_Core.WDItemEngine.log("INFO", format_msg(record_id, record_prop, wd_item.wd_item_id, msg))
    except Exception as e:
        print(e)
        PBB_Core.WDItemEngine.log("ERROR", format_msg(record_id, record_prop, wd_item.wd_item_id, str(e), type(e)))


def format_msg(external_id, external_id_prop, wdid, msg, msg_type=None):
    """
    Format message for logging
    :return: str
    """
    # escape double quotes and quote string with commas,
    # so it can be read by pd.read_csv(fp, escapechar='\\')
    msg = msg.replace("\"", "\\\"")
    msg = "\"" + msg + "\"" if "," in msg else msg
    msg = msg.replace(",", "")
    s = '{},{},{},{},{}'.format(external_id, external_id_prop, wdid, msg, msg_type)
    return s


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

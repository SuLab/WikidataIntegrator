import difflib
import datetime
import json
from collections import defaultdict, Counter
from time import gmtime, strftime

import pandas as pd
import requests
from dateutil import parser as du

from wikidataintegrator.ref_handlers import update_retrieved_if_new
from . import wdi_core
from .wdi_core import WDItemEngine, WDApiError
from wikidataintegrator.wdi_config import config

# https://www.wikidata.org/wiki/Property:P4390
RELATIONS = {'close': 'Q39893184',
             'exact': 'Q39893449',
             'related': 'Q39894604',
             'broad': 'Q39894595',
             'narrow': 'Q39893967'}

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

    _release_cache = defaultdict(dict)
    _database_cache = dict()

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

    @classmethod
    def lookup_database(cls, edition_of):
        if edition_of in cls._database_cache:
            return cls._database_cache[edition_of]

        query = """SELECT ?item ?itemLabel WHERE {
                    ?item wdt:P31 wd:Q4117139 .
                    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
                }"""
        results = WDItemEngine.execute_sparql_query(query)
        db_item_map = {x['itemLabel']['value']: x['item']['value'].replace('http://www.wikidata.org/entity/', '') for x
                       in results['results']['bindings']}
        if edition_of not in db_item_map:
            raise ValueError("Database {} not found in wikidata. Please provide edition_of_wdid".format(edition_of))

        cls._database_cache[edition_of] = db_item_map[edition_of]
        return db_item_map[edition_of]

    def make_statements(self):
        s = []
        # instance of edition
        s.append(wdi_core.WDItemID('Q3331189', 'P31'))
        # edition or translation of
        s.append(wdi_core.WDItemID(self.edition_of_wdid, 'P629'))
        # edition number
        s.append(wdi_core.WDString(self.edition, 'P393'))

        if self.archive_url:
            s.append(wdi_core.WDUrl(self.archive_url, 'P1065'))

        if self.pub_date:
            s.append(wdi_core.WDTime(self.pub_date, 'P577', precision=self.date_precision))

        self.statements = s

    def get_or_create(self, login=None):

        # check in cache
        if self.edition_of_wdid in self._release_cache and self.edition in self._release_cache[self.edition_of_wdid]:
            return self._release_cache[self.edition_of_wdid][self.edition]

        # check in wikidata
        edition_dict = id_mapper("P393", (("P629", self.edition_of_wdid), ("P31", "Q3331189")))
        if edition_dict and self.edition in edition_dict:
            # add to cache
            self._release_cache[self.edition_of_wdid][self.edition] = edition_dict[self.edition]
            return edition_dict[self.edition]

        # create new
        if login is None:
            raise ValueError("login required to create item")
        item = wdi_core.WDItemEngine(item_name=self.title, data=self.statements, domain="release")
        item.set_label(self.title)
        item.set_description(description=self.description, lang='en')
        write_success = try_write(item, self.edition + "|" + self.edition_of_wdid, 'P393|P629', login)
        if write_success:
            # add to cache
            self._release_cache[self.edition_of_wdid][self.edition] = item.wd_item_id
            return item.wd_item_id
        else:
            raise write_success


class PubmedItem(object):
    """
    Get or create a wikidata item stub given a pubmed ID

    Usage:
    PubmedItem(22674334).get_or_create(login)

    Data source: Europepmc
    API: https://europepmc.org/RestfulWebService
    Doc: https://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf

    wikidata Item format
    general guidelines: https://www.wikidata.org/wiki/Help:Sources
    more specific to journal articles: https://github.com/mitar/bib2wikidata/issues/1#issuecomment-50998834
    modelling after: https://www.wikidata.org/wiki/Q21093381 because it has both authors and author name strings

    This will add authors, if they have orcid IDs AND the item already exists in wikidata

    https://www.wikidata.org/wiki/Wikidata:WikiProject_Source_MetaData/Bibliographic_metadata_for_scholarly_articles_in_Wikidata

    """

    _cache = dict()
    PROPS = {
        'instance of': 'P31',
        'title': 'P1476',
        'published in': 'P1433',
        'volume': 'P478',
        'publication date': 'P577',
        'page(s)': 'P304',
        'issue': 'P433',
        'author name string': 'P2093',
        'author': 'P50',
        'PubMed ID': 'P698',
        'MED': 'P698',
        'DOI': 'P356',
        'series ordinal': 'P1545',
        'PMCID': 'P932',
        'PMC': 'P932',
        'reference URL': 'P854'
    }

    id_types = {"MED": "PubMed ID",
                "PMC": "PMC",
                "DOI": "DOI"}

    pubtypes = {"research-article": "Q13442814",  # scientific article
                "Journal Article": "Q13442814",  # scientific article
                }
    descriptions = {'Q13442814': 'scientific article'}

    def __init__(self, ext_id, id_type="MED"):
        self.warnings = []
        self.errors = []
        assert id_type in self.id_types, "id_type must be in {}".format(self.id_types)
        self.ext_id = str(ext_id)
        self.id_type = id_type
        self.meta = {
            'title': None,
            'doi': None,
            'volume': None,
            'issue': None,
            'journal_wdid': None,
            'journal_issn': None,
            'type': None,
            'date': None,
            'pages': None,
            'authors': None,
            'pubtypes': None,
            'pubtype_qid': None,
            'parsed': False
        }
        if self.id_type == "PMC" and self.ext_id.startswith("PMC"):
            self.ext_id = self.ext_id.replace("PMC", "")

        self.reference = None
        self.statements = None
        self.wdid = None
        self.article = None
        self.user_agent = config['USER_AGENT_DEFAULT']

    def get_article_info(self):
        if self.id_type == "PMC":
            url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:PMC{}&resulttype=core&format=json'
            url = url.format(self.ext_id)
        elif self.id_type == "DOI":
            url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22{}%22&resulttype=core&format=json"
            url = url.format(self.ext_id)
        else:
            url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{}%20AND%20SRC:{}&resulttype=core&format=json'
            url = url.format(self.ext_id, self.id_type)
        headers = {
            'User-Agent': self.user_agent
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        d = response.json()
        if d['hitCount'] != 1:
            raise ValueError("No results")
        self.article = d['resultList']['result'][0]

    def parse_metadata(self):
        if not self.article:
            self.get_article_info()

        self.meta['pmid'] = self.article.get('pmid','')
        self.meta['pmcid'] = self.article.get('pmcid', '').replace("PMC", "")
        self.meta['title'] = self.article['title'][:249]
        if 'pubTypeList' in self.article:
            pubtypes = self.article['pubTypeList']['pubType']
            if not isinstance(pubtypes, list):
                pubtypes = [pubtypes]
            self.meta['pubtypes'] = pubtypes
        else:
            self.meta['pubtypes'] = ['research-article']
            self.warnings.append("unknown publication type, assuming scientific article")
            print("unknown publication type, assuming scientific article")
        self.meta['pubtype_qid'] = list(set(self.pubtypes.get(x, "Q13442814") for x in self.meta['pubtypes']))
        if len(self.meta['pubtype_qid']) < 1:
            self.errors.append("unknown publication type: {}".format(self.meta['pubtypes']))
            raise ValueError("unknown publication type: {}".format(self.meta['pubtypes']))

        if 'issn' in self.article['journalInfo']['journal']:
            self.meta['journal_issn'] = self.article['journalInfo']['journal']['issn']  # published in
        elif 'essn' in self.article['journalInfo']['journal']:
            self.meta['journal_issn'] = self.article['journalInfo']['journal']['essn']  # published in
        else:
            msg = "unknown journal: {}".format(self.article['journalInfo']['journal'])
            self.errors.append(msg)
            print(msg)

        self.meta['journal_wdid'] = prop2qid("P236", self.meta['journal_issn'])
        if not self.meta['journal_wdid']:
            raise ValueError("journal not found: {}".format(self.meta['journal_issn']))
        self.meta['date'] = du.parse(self.article['firstPublicationDate']).strftime('+%Y-%m-%dT%H:%M:%SZ')

        authors = []
        for author in self.article['authorList']['author']:
            if 'firstName' in author and 'lastName' in author:
                authors.append(author['firstName'] + ' ' + author['lastName'])
            elif 'fullName' in author:
                authors.append(author['fullName'])
            elif 'collectiveName' in author:
                authors.append(author['collectiveName'])
            else:
                msg = "unknown author: {}".format(author)
                print(msg)
                self.errors.append(msg)
                authors.append(None)

        self.meta['authors'] = authors
        self.meta['author_orcid'] = {author: x['authorId']['value'] for author, x in
                                     zip(authors, self.article['authorList']['author']) if
                                     'authorId' in x and x['authorId']['type'] == 'ORCID'}
        self.meta['author_qid'] = {author: PubmedItem.lookup_author(orcid) for author, orcid in
                                   self.meta['author_orcid'].items()}

        # optional
        self.meta['volume'] = self.article['journalInfo'].get('volume')
        self.meta['issue'] = self.article['journalInfo'].get('issue')
        self.meta['pages'] = self.article.get('pageInfo')
        self.meta['doi'] = self.article.get('doi')
        self.meta['parsed'] = True

    @staticmethod
    def lookup_author(orcid_id):
        return prop2qid("P496", orcid_id)

    def make_reference(self):
        if not self.meta['parsed']:
            self.parse_metadata()
        if 'pmcid' in self.meta and self.meta['pmcid']:
            extid = wdi_core.WDString(value=self.meta['pmcid'], prop_nr=self.PROPS['PMCID'], is_reference=True)
            ref_url = wdi_core.WDUrl("http://europepmc.org/abstract/{}/{}".format("PMC", self.meta['pmcid']),
                                     self.PROPS['reference URL'], is_reference=True)
        elif 'pmid' in self.meta and self.meta['pmid']:
            extid = wdi_core.WDString(value=self.meta['pmid'], prop_nr=self.PROPS['PubMed ID'], is_reference=True)
            ref_url = wdi_core.WDUrl("http://europepmc.org/abstract/{}/{}".format("MED", self.meta['pmid']),
                                     self.PROPS['reference URL'], is_reference=True)
        elif 'doi' in self.meta and self.meta['doi']:
            extid = wdi_core.WDString(value=self.meta['doi'], prop_nr=self.PROPS['DOI'], is_reference=True)
            ref_url = None
        else:
            raise ValueError("ref needs a pmcid, pmid, or doi")
        stated_in = wdi_core.WDItemID(value='Q5412157', prop_nr='P248', is_reference=True)
        retrieved = wdi_core.WDTime(strftime("+%Y-%m-%dT00:00:00Z", gmtime()), prop_nr='P813', is_reference=True)
        self.reference = [stated_in, extid, retrieved]
        if ref_url:
            self.reference.append(ref_url)

    def make_author_statements(self, ordinals=None):
        """
        ordinals is a list of ordinals to NOT include
        use this to update an existing item that may have authors, so you don't want to
        add the author string for them
        :param ordinals: if None, include all authors
        :return:
        """
        s = []
        for n, author in enumerate(self.meta['authors'], 1):
            if ordinals is not None and n in ordinals:
                continue
            series_ordinal = wdi_core.WDString(str(n), self.PROPS['series ordinal'], is_qualifier=True)
            if author in self.meta['author_orcid']:
                if self.meta['author_qid'][author]:
                    s.append(wdi_core.WDItemID(self.meta['author_qid'][author], self.PROPS['author'],
                                               references=[self.reference], qualifiers=[series_ordinal]))
                else:
                    msg = "No Author found for author: {}, orcid: {}".format(author, self.meta['author_orcid'][author])
                    self.warnings.append(msg)
                    print(msg)
                    s.append(wdi_core.WDString(author, self.PROPS['author name string'],
                                               references=[self.reference], qualifiers=[series_ordinal]))
            elif author:
                s.append(wdi_core.WDString(author, self.PROPS['author name string'],
                                           references=[self.reference], qualifiers=[series_ordinal]))
        return s

    def make_statements(self, ordinals=None):
        """

        :param ordinals: passed to self.make_author_statements
        :return:
        """
        self.make_reference()
        s = []

        ### Required statements
        for pubtype in self.meta['pubtype_qid']:
            s.append(wdi_core.WDItemID(pubtype, self.PROPS['instance of'], references=[self.reference]))
        s.append(wdi_core.WDMonolingualText(self.meta['title'], self.PROPS['title'], references=[self.reference]))
        s.append(wdi_core.WDTime(self.meta['date'], self.PROPS['publication date'], references=[self.reference]))
        s.append(wdi_core.WDItemID(self.meta['journal_wdid'], self.PROPS['published in'], references=[self.reference]))
        s.extend(self.make_author_statements(ordinals=ordinals))

        ### Optional statements
        if self.meta['pmid']:
            s.append(wdi_core.WDExternalID(self.meta['pmid'], self.PROPS['PubMed ID'], references=[self.reference]))
        if self.meta['volume']:
            s.append(wdi_core.WDString(self.meta['volume'], self.PROPS['volume'], references=[self.reference]))
        if self.meta['pages']:
            s.append(wdi_core.WDString(self.meta['pages'], self.PROPS['page(s)'], references=[self.reference]))
        if self.meta['issue']:
            s.append(wdi_core.WDString(self.meta['issue'], self.PROPS['issue'], references=[self.reference]))
        if self.meta['doi']:
            s.append(wdi_core.WDExternalID(self.meta['doi'].upper(), self.PROPS['DOI'], references=[self.reference]))
        if self.meta['pmcid']:
            s.append(wdi_core.WDExternalID(self.meta['pmcid'].replace("PMC", ""), self.PROPS['PMCID'],
                                           references=[self.reference]))

        self.statements = s

    def update(self, login, qid=None):
        if not qid:
            qid = self.check_if_exists()
            if not qid:
                raise ValueError("item doesn't exist")

        try:
            self.parse_metadata()
        except Exception as e:
            print(e)
            return None

        # we need the json of the item to grab any existing authors
        url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={}&format=json".format(qid)
        headers = {
            'User-Agent': self.user_agent
        }
        dc = requests.get(url, headers=headers).json()
        claims = dc['entities'][qid]['claims']
        if 'P50' not in claims:
            ordinals = None
        else:
            ordinals = []
            if not isinstance(claims['P50'], list):
                claims['P50'] = [claims['P50']]
            for claim in claims['P50']:
                assert len(claim['qualifiers']['P1545']) == 1
                ordinals.append(int(claim['qualifiers']['P1545'][0]['datavalue']['value']))
        try:
            current_label = dc['entities'][qid]['labels']['en']['value']
        except KeyError:
            current_label = ''
        if difflib.SequenceMatcher(None, current_label, self.meta['title']).ratio() > 0.90:
            self.meta['title'] = current_label

        # make statements without the existing authors
        self.make_statements(ordinals)

        item = wdi_core.WDItemEngine(wd_item_id=qid, data=self.statements, domain="scientific_article",
                                     global_ref_mode='CUSTOM', ref_handler=update_retrieved_if_new)
        item.set_label(self.meta['title'])
        description = ', '.join(self.descriptions[x] for x in self.meta['pubtype_qid'])
        if item.get_description() == '':
            item.set_description(description, lang='en')
        write_success = try_write(item, self.ext_id, self.PROPS[self.id_types[self.id_type]], login)
        if write_success:
            self._cache[(self.ext_id, self.id_type)] = item.wd_item_id
            return item.wd_item_id
        else:
            return None

    def create(self, login=None):
        """
        Attempt to create new item. Returns `None` if creation fails.
        """
        if login is None:
            raise ValueError("login required to create item")

        try:
            self.parse_metadata()
            self.make_statements()
            item = wdi_core.WDItemEngine(item_name=self.meta['title'], data=self.statements,
                                         domain="scientific_article")
        except Exception as e:
            msg = format_msg(self.ext_id, self.id_type, None, str(e), type(e))
            print(msg)
            wdi_core.WDItemEngine.log("ERROR", msg)
            return None

        item.set_label(self.meta['title'])
        description = ', '.join(self.descriptions[x] for x in self.meta['pubtype_qid'])
        item.set_description(description, lang='en')
        write_success = try_write(item, self.ext_id, self.PROPS[self.id_types[self.id_type]], login)
        if write_success:
            self._cache[(self.ext_id, self.id_type)] = item.wd_item_id
            return item.wd_item_id
        else:
            return None

    def check_if_exists(self):
        if self.id_type not in self.PROPS:
            raise ValueError("can't check if IDs of this property type are in Wikidata")
        prop = self.PROPS[self.id_type]
        wdid = prop2qid(prop, self.ext_id)
        if wdid:
            self._cache[(self.ext_id, self.id_type)] = wdid
            return wdid

    def get_or_create(self, login=None):
        """
        Returns wdid if item exists or is created
        If the item exists, but not with the external ID provided, the item is updated
        returns None if the pmid is not found
        returns None and logs the exception if there is a write failure

        :param login: required to create an item
        :return:
        """
        # check if in local cache
        if (self.ext_id, self.id_type) in self._cache:
            return self._cache[(self.ext_id, self.id_type)]
        # check if exists in wikidata
        qid_if_exists = self.check_if_exists()
        if qid_if_exists:
            return qid_if_exists

        # additional check, its possible the item exists in wikidata, but not with this ID type
        # for example, PubmedItem may have been constructed with a PMCID, the wikidata item may have a PMID but not
        # a PMCID, so check the other external IDs
        try:
            self.parse_metadata()
        except Exception as e:
            print(e)
            return None
        ids = {"MED": self.meta['pmid'],
               "PMC": self.meta['pmcid'],
               "DOI": self.meta['doi']}
        for id_type, i in ids.items():
            if id_type == self.id_type:
                # dont check the one we already checked
                continue
            qid = prop2qid(self.PROPS[id_type], i)
            if qid:
                return self.update(login, qid=qid)

        # item doesn't exist.
        return self.create(login=login)


def try_write(wd_item, record_id, record_prop, login, edit_summary='', write=True):
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
    :param write: If `False`, do not actually perform write. Action will be logged as if write had occured
    :type write: bool
    :return: True if write did not throw an exception, returns the exception otherwise
    """
    if wd_item.require_write:
        if wd_item.create_new_item:
            msg = "CREATE"
        else:
            msg = "UPDATE"
    else:
        msg = "SKIP"

    try:
        if write:
            wd_item.write(login=login, edit_summary=edit_summary)
        wdi_core.WDItemEngine.log("INFO", format_msg(record_id, record_prop, wd_item.wd_item_id, msg) + ";" + str(
            wd_item.lastrevid))
    except WDApiError as e:
        print(e)
        wdi_core.WDItemEngine.log("ERROR",
                                  format_msg(record_id, record_prop, wd_item.wd_item_id, json.dumps(e.wd_error_msg),
                                             type(e)))
        return e
    except Exception as e:
        print(e)
        wdi_core.WDItemEngine.log("ERROR", format_msg(record_id, record_prop, wd_item.wd_item_id, str(e), type(e)))
        return e

    return True


def format_msg(external_id, external_id_prop, wdid, msg, msg_type=None, delimiter=";"):
    """
    Format message for logging
    :return: str
    """
    fmt = ('{}' + delimiter) * 4 + '{}'  # '{};{};{};{};{}'
    d = {'external_id': external_id,
         'external_id_prop': external_id_prop,
         'wdid': wdid,
         'msg': msg,
         'msg_type': msg_type}
    for k, v in d.items():
        if isinstance(v, str) and delimiter in v and '"' in v:
            v = v.replace('"', "'")
        if isinstance(v, str) and delimiter in v:
            d[k] = '"' + v + '"'

    s = fmt.format(d['external_id'], d['external_id_prop'], d['wdid'], d['msg'], d['msg_type'])
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


def id_mapper(prop, filters=None, raise_on_duplicate=False, return_as_set=False, prefer_exact_match=False):
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
    :param raise_on_duplicate: If an ID is found on more than one wikidata item, what action to take?
        This is equivalent to the Distinct values constraint. e.g.: http://tinyurl.com/ztpncyb
        Note that a wikidata item can have more than one ID. This is not checked for
        True: raise ValueError
        False: only one of the values is kept if there are duplicates (unless return_as_set if True)
    :type raise_on_duplicate: bool
    :param return_as_set: If True, all values in the returned dict will be a set of strings
    :type return_as_set: bool
    :param prefer_exact_match: If True, the mapping relation type qualifier will be queried. If an ID mapping has
    multiple values, the ones marked as an 'exactMatch' will be returned while the others discarded. If none have
    an exactMatch qualifier, all will be returned. If multiple has 'exactMatch', they will not be discarded.
    https://www.wikidata.org/wiki/Property:P4390
    :type prefer_exact_match: bool


    If `raise_on_duplicate` is False and `return_as_set` is True, the following can be returned:
    { 'A0KH68': {'Q23429083'}, 'B023F44': {'Q237623', 'Q839742'} }

    :return: dict

    """
    query = "SELECT ?id ?item ?mrt WHERE {"
    query += "?item p:{} ?s .\n?s ps:{} ?id .\n".format(prop, prop)
    query += "OPTIONAL {?s pq:P4390 ?mrt}\n"
    if filters:
        for f in filters:
            query += "?item wdt:{} wd:{} .\n".format(f[0], f[1])
    query = query + "}"
    results = WDItemEngine.execute_sparql_query(query)['results']['bindings']
    results = [{k: v['value'] for k, v in x.items()} for x in results]
    for r in results:
        r['item'] = r['item'].split('/')[-1]
        if 'mrt' in r:
            r['mrt'] = r['mrt'].split('/')[-1]
    if not results:
        return None

    if prefer_exact_match:
        df = pd.DataFrame(results)
        if 'mrt' not in df:
            df['mrt'] = ''
        df.mrt = df.mrt.fillna('')
        df['keep'] = True

        # check if a QID has more than one extID
        # i.e single value constraint
        # example: https://www.wikidata.org/w/index.php?title=Q3840916&oldid=645203228#P486 (D018311)
        # example 2: https://www.wikidata.org/w/index.php?title=Q388113&oldid=648588555#P486 (D000037, D000033)
        df.sort_values("item", inplace=True)
        dupe_df = df[df.duplicated(subset=["item"], keep=False)]
        for item, subdf in dupe_df.groupby("item"):
            # if there is one with exact match, take it, otherwise, skip
            if sum(subdf.mrt == RELATIONS['exact']) == 1:
                df.loc[(df.item == item) & (df.mrt != RELATIONS['exact']), 'keep'] = False

        # check if a extID has more than one QID
        # example: https://www.wikidata.org/w/index.php?title=Q846227&oldid=648565663#P486
                    # https://www.wikidata.org/w/index.php?title=Q40207875&oldid=648565770#P486
        df.sort_values("id", inplace=True)
        dupe_df = df[df.duplicated(subset=["id"], keep=False)]
        for ext_id, subdf in dupe_df.groupby("id"):
            # if there is one with exact match, take it, otherwise, skip
            if sum(subdf.mrt == RELATIONS['exact']) == 1:
                df.loc[(df.id == ext_id) & (df.mrt != RELATIONS['exact']), 'keep'] = False

        df = df[df.keep]
        results = df.to_dict("records")

    id_qid = defaultdict(set)
    for r in results:
        id_qid[r['id']].add(r['item'])
    dupe = {k:v for k,v in id_qid.items() if len(v)>1}
    if raise_on_duplicate and dupe:
        raise ValueError("duplicate ids: {}".format(dupe))

    if return_as_set:
        return dict(id_qid)
    else:
        return {x['id']: x['item'] for x in results}
import datetime
import json
from collections import defaultdict, Counter
from time import gmtime, strftime

import requests
from dateutil import parser as du

from . import wdi_core
from .wdi_core import WDItemEngine, WDApiError


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
    PubmedStub(22674334).get_or_create(login)

    Data source: https://www.mediawiki.org/wiki/Citoid/API
    example:
    https://citoid.wikimedia.org/api?search=https://www.ncbi.nlm.nih.gov/pubmed/13054692&format=zotero

    wikidata Item format
    general guidelines: https://www.wikidata.org/wiki/Help:Sources
    more specific to journal articles: https://github.com/mitar/bib2wikidata/issues/1#issuecomment-50998834
    modelling after: https://www.wikidata.org/wiki/Q21093381 because it has both authors and author name strings

    This will not add authors, it will only add author name strings, as I do not habve enough information to assume
    they are the same as author items that exist.

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
        'PubMed ID': 'P698',
        'DOI': 'P356',
        'series ordinal': 'P1545',
    }

    # can be expanded to books and such...
    instance_of_items = {'journalArticle': 'Q13442814'}
    descriptions = {'journalArticle': 'scientific journal article'}

    def __init__(self, pmid):
        self.pmid = str(pmid)
        self.meta = {
            'title': None,
            'dois': None,
            'volume': None,
            'issue': None,
            'journal_wdid': None,
            'journal_issn': None,
            'type': None,
            'date': None,
            'pages': None,
            'authors': None,
        }

        self.reference = None
        self.statements = None
        self.wdid = None
        self.citoid = None

    def _valid_pmid(self):
        url = 'https://citoid.wikimedia.org/api?search=https://www.ncbi.nlm.nih.gov/pubmed/{}&format=zotero'.format(
            self.pmid)
        self.citoid = requests.get(url).json()[0]
        return True if self.citoid['itemType'] in self.instance_of_items else False

    def get_metadata(self):

        if not self._valid_pmid():
            raise ValueError("error getting metadata: {}".format(self.pmid))

        # todo: original language of work not in citoid response
        self.meta['title'] = self.citoid['title'][:249]
        self.meta['type'] = self.citoid['itemType']  # instance of. values = {'journalArticle', .. }
        self.meta['journal_issn'] = self.citoid['ISSN']  # published in
        self.meta['date'] = du.parse(self.citoid['date']).strftime('+%Y-%m-%dT%H:%M:%SZ')
        self.meta['authors'] = [x['firstName'] + " " + x['lastName'] for x in self.citoid['creators'] if
                                x['creatorType'] == 'author']

        # optional
        self.meta['volume'] = self.citoid.get('volume', None)
        self.meta['pages'] = self.citoid.get('pages', None)
        self.meta['issue'] = self.citoid.get('issue', None)
        self.meta['dois'] = self.citoid.get('DOI', None)

        # also validate response here
        if self.meta['dois']:
            assert isinstance(self.meta['dois'], str)
        self.meta['journal_wdid'] = prop2qid("P236", self.meta['journal_issn'])
        if not self.meta['journal_wdid']:
            raise ValueError("journal not found: {}".format(self.meta['journal_issn']))

    def make_reference(self):
        stated_in = wdi_core.WDItemID(value='Q180686', prop_nr='P248', is_reference=True)
        pmid = wdi_core.WDString(value=self.pmid, prop_nr='P698', is_reference=True)
        retrieved = wdi_core.WDTime(strftime("+%Y-%m-%dT00:00:00Z", gmtime()), prop_nr='P813', is_reference=True)
        self.reference = [stated_in, pmid, retrieved]

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
        s.append(wdi_core.WDExternalID(self.pmid, self.PROPS['PubMed ID'], references=[self.reference]))
        s.append(wdi_core.WDItemID(self.instance_of_items[self.meta['type']], self.PROPS['instance of'],
                                   references=[self.reference]))
        s.append(wdi_core.WDMonolingualText(self.meta['title'], self.PROPS['title'], references=[self.reference]))
        s.append(wdi_core.WDTime(self.meta['date'], self.PROPS['publication date'], references=[self.reference]))
        s.append(wdi_core.WDItemID(self.meta['journal_wdid'], self.PROPS['published in'], references=[self.reference]))
        s.extend(self.make_author_statements(ordinals=ordinals))

        ### Optional statements
        if self.meta['volume']:
            s.append(wdi_core.WDString(self.meta['volume'], self.PROPS['volume'], references=[self.reference]))
        if self.meta['pages']:
            s.append(wdi_core.WDString(self.meta['pages'], self.PROPS['page(s)'], references=[self.reference]))
        if self.meta['issue']:
            s.append(wdi_core.WDString(self.meta['issue'], self.PROPS['issue'], references=[self.reference]))
        if self.meta['dois']:
            s.append(wdi_core.WDExternalID(self.meta['dois'].upper(), self.PROPS['DOI'], references=[self.reference]))

        self.statements = s

    def update(self, wdid, login):
        # we need the json of the item to grab any existing authors
        url = "https://www.wikidata.org/w/api.php?action=wbgetentities&ids={}&format=json".format(wdid)
        dc = requests.get(url).json()
        claims = dc['entities'][wdid]['claims']
        if 'P50' not in claims:
            ordinals = None
        else:
            ordinals = []
            if not isinstance(claims['P50'], list):
                claims['P50'] = [claims['P50']]
            for claim in claims['P50']:
                assert len(claim['qualifiers']['P1545']) == 1
                ordinals.append(int(claim['qualifiers']['P1545'][0]['datavalue']['value']))

        # validate pmid is on item
        if 'P698' not in claims:
            raise ValueError("unknown pubmed id")
        if len(claims['P698']) != 1:
            raise ValueError("more than one pmid")
        item_pmid = claims['P698'][0]['mainsnak']['datavalue']['value']
        if item_pmid != self.pmid:
            raise ValueError("pmids don't match")

        try:
            self.get_metadata()
        except Exception as e:
            print(e)
            return None
        self.make_statements(ordinals)

        item = wdi_core.WDItemEngine(wd_item_id=wdid, data=self.statements, domain="scientific_article")
        item.set_label(self.meta['title'])
        item.set_description(description=self.descriptions[self.meta['type']], lang='en')
        write_success = try_write(item, self.pmid, 'P698', login)
        if write_success:
            self._cache[self.pmid] = item.wd_item_id
            return item.wd_item_id
        else:
            return None

    def create(self, login=None):
        # create new item
        if login is None:
            raise ValueError("login required to create item")

        try:
            self.get_metadata()
        except Exception as e:
            print(e)
            return None
        self.make_statements()

        item = wdi_core.WDItemEngine(item_name=self.meta['title'], data=self.statements, domain="scientific_article")
        item.set_label(self.meta['title'])
        item.set_description(description=self.descriptions[self.meta['type']], lang='en')
        write_success = try_write(item, self.pmid, 'P698', login)
        if write_success:
            self._cache[self.pmid] = item.wd_item_id
            return item.wd_item_id
        else:
            return None

    def get_or_create(self, login=None):
        """
        Returns wdid if item exists or is created
        returns None if the pmid is not found
        returns None and logs the exception if there is a write failure

        :param login: required to create an item
        :return:
        """
        # check if in local cache
        if self.pmid in self._cache:
            return self._cache[self.pmid]
        # check if exists in wikidata
        wdid = prop2qid('P698', self.pmid)
        if wdid:
            self._cache[self.pmid] = wdid
            return wdid

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
        wdi_core.WDItemEngine.log("INFO", format_msg(record_id, record_prop, wd_item.wd_item_id, msg))
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
    s = fmt.format(external_id, external_id_prop, wdid, msg, msg_type)
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


def id_mapper(prop, filters=None, raise_on_duplicate=False, return_as_set=False):
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
        False: only one of the values is kept if there are duplicates
    :type raise_on_duplicate: bool
    :param return_as_set: If True, all values in the returned dict will be a set of strings
    :type return_as_set: bool

    If `raise_on_duplicate` is False and `return_as_set` is True, the following can be returned:
    { 'A0KH68': {'Q23429083'}, 'B023F44': {'Q237623', 'Q839742'} }

    :return: dict

    """
    query = "SELECT * WHERE {"
    query += "?item wdt:{} ?id .\n".format(prop)
    if filters:
        for f in filters:
            query += "?item wdt:{} wd:{} .\n".format(f[0], f[1])
    query = query + "}"
    results = WDItemEngine.execute_sparql_query(query)['results']['bindings']
    if not results:
        return None

    ids = [x['id']['value'] for x in results]
    if raise_on_duplicate and len(ids) != len(set(ids)):
        dupe_ids = [x for x, count in Counter(ids).items() if count > 1]
        raise ValueError("duplicate ids: {}".format(
            [(x['id']['value'], x['item']['value']) for x in results if x['id']['value'] in dupe_ids]))

    if return_as_set:
        d = defaultdict(set)
        for x in results:
            d[x['id']['value']].add(x['item']['value'].split('/')[-1])
        return dict(d)
    else:
        return {x['id']['value']: x['item']['value'].split('/')[-1] for x in results}

import difflib
import datetime
import json
from collections import defaultdict, Counter
from time import gmtime, strftime, sleep

import pandas as pd
from tqdm import tqdm
import requests
from dateutil import parser as du

from wikidataintegrator.ref_handlers import update_retrieved_if_new, update_retrieved_if_new_multiple_refs
from . import wdi_core
from .wdi_core import WDItemEngine, WDApiError, WDBaseDataType
from wikidataintegrator.wdi_config import config

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
    'reference URL': 'P854',
    'ISSN': 'P236',
    'ISBN-13': 'P212',
    'orcid id': "P496",
    'stated in': "P248",
    'retrieved': 'P813'
}

# https://www.wikidata.org/wiki/Property:P4390
RELATIONS = {
    'close': 'Q39893184',
    'exact': 'Q39893449',
    'related': 'Q39894604',
    'broad': 'Q39894595',
    'narrow': 'Q39893967'
}


class MappingRelationHelper:
    ABV_MRT = {
        "close": "http://www.w3.org/2004/02/skos/core#closeMatch",
        "exact": "http://www.w3.org/2004/02/skos/core#exactMatch",
        "related": "http://www.w3.org/2004/02/skos/core#relatedMatch",
        "broad": "http://www.w3.org/2004/02/skos/core#broadMatch",
        "narrow": "http://www.w3.org/2004/02/skos/core#narrowMatch"
    }

    def __init__(self, sparql_endpoint_url='https://query.wikidata.org/sparql'):
        h = WikibaseHelper(sparql_endpoint_url=sparql_endpoint_url)
        self.mrt_pid = h.get_pid("http://www.w3.org/2004/02/skos/core#mappingRelation")
        try:
            self.mrt_qids = {x: h.get_qid(x) for x in self.ABV_MRT.values()}
        except KeyError as e:
            print("{} not found. resorting to known wikidata QIDs".format(e))
            self.mrt_qids = {self.ABV_MRT[k]: v for k, v in RELATIONS.items()}

    def set_mrt(self, s: WDBaseDataType, mrt: str):
        """
        accepts a statement and adds a qualifer setting the mrt
        modifies s in place
        :param s: a WDBaseDataType statement
        :param mrt: one of {'close', 'broad', 'exact', 'related', 'narrow'}
        :return: s
        """
        valid_mrts_abv = self.ABV_MRT.keys()
        valid_mrts_uri = self.ABV_MRT.values()
        if mrt in valid_mrts_abv:
            mrt_uri = self.ABV_MRT[mrt]
        elif mrt in valid_mrts_uri:
            mrt_uri = mrt
        else:
            raise ValueError("mrt must be one of {}, found {}".format(valid_mrts_abv, mrt))
        mrt_qid = self.mrt_qids[mrt_uri]

        q = wdi_core.WDItemID(mrt_qid, self.mrt_pid, is_qualifier=True)
        s.qualifiers.append(q)
        return s


class WikibaseHelper:
    """
    Helper functions for accessing PIDs and QIDs across wikibases

    This functionality depends upon their existing two properties: equivalent property and equivalent class
    with the equivalent property values: 'http://www.w3.org/2002/07/owl#equivalentProperty' and
    'http://www.w3.org/2002/07/owl#equivalentClass' respectively
    """

    def __init__(self, sparql_endpoint_url='https://query.wikidata.org/sparql'):
        self.sparql_endpoint_url = sparql_endpoint_url
        # a map of property URIs to a PID in the wikibase you are using
        uri_pid = id_mapper(self.guess_equivalent_property_pid(), endpoint=self.sparql_endpoint_url,
                            return_as_set=True)
        # remove duplicates/conflicts
        self.URI_PID = {k: list(v)[0] for k, v in uri_pid.items() if len(v) == 1}
        # get equivalent class PID
        equiv_class_pid = self.URI_PID['http://www.w3.org/2002/07/owl#equivalentClass']
        # a map of item URIs to a QID in the wikibase you are using
        uri_qid = id_mapper(equiv_class_pid, endpoint=self.sparql_endpoint_url,
                            return_as_set=True)
        # remove duplicates/conflicts
        self.URI_QID = {k: list(v)[0] for k, v in uri_qid.items() if len(v) == 1}

    def guess_equivalent_property_pid(self):
        # get the equivalent property PID without knowing the PID for equivalent property!!!
        query = '''SELECT * WHERE {
          ?item ?prop <http://www.w3.org/2002/07/owl#equivalentProperty> .
          ?item <http://wikiba.se/ontology#directClaim> ?prop .
        }'''
        pid = wdi_core.WDItemEngine.execute_sparql_query(query, endpoint=self.sparql_endpoint_url)
        pid = pid['results']['bindings'][0]['prop']['value']
        pid = pid.split("/")[-1]
        return pid

    def get_pid(self, uri):
        """
        Get the pid for the property in this wikibase instance ( the one at `sparql_endpoint_url` ),
         that corresponds to (i.e. has the equivalent property) `uri`
        """
        # if the wikibase is wikidata, and we give a wikidata uri or a PID with no URI specified:
        if (self.sparql_endpoint_url == 'https://query.wikidata.org/sparql' and
                (uri.startswith("P") or uri.startswith("http://www.wikidata.org/entity/"))):
            # don't look up anything, just return the same value
            return uri
        if uri.startswith("P"):
            uri = "http://www.wikidata.org/entity/" + uri
        return self.URI_PID[uri]

    def get_qid(self, uri):
        # if the wikibase is wikidata, and we give a wikidata uri or a QID with no URI specified:
        if (self.sparql_endpoint_url == 'https://query.wikidata.org/sparql' and
                (uri.startswith("Q") or uri.startswith("http://www.wikidata.org/entity/"))):
            # don't look up anything, just return the same value
            return uri
        if uri.startswith("Q"):
            uri = "http://www.wikidata.org/entity/" + uri
        return self.URI_QID[uri]


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
    r = wdi_helpers.Release("Ensembl Release 85", "Release 85 of Ensembl", "85", edition_of_qid="Q1234",
                            archive_url="http://jul2016.archive.ensembl.org/",
                            pub_date='+2016-07-01T00:00:00Z', date_precision=10)
    r.get_or_create(login)

    """
    # dict. key is a tuple of (sparql_endpoint_url, edition_of_qid, edition), value is the qid of that release
    _release_cache = dict()

    def __init__(self, title, description, edition, edition_of_wdid, archive_url=None,
                 pub_date=None, date_precision=11, mediawiki_api_url='https://www.wikidata.org/w/api.php',
                 sparql_endpoint_url='https://query.wikidata.org/sparql'):
        """

        :param title: title of release item
        :type title: str
        :param description: description of release item
        :type description: str
        :param edition: edition number or unique identifier for the release
        :type edition: str
        :param edition_of_wdid: wikidata qid of database this release is a release of
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
        self.edition_of_qid = edition_of_wdid
        self.sparql_endpoint_url = sparql_endpoint_url
        self.mediawiki_api_url = mediawiki_api_url
        self.helper = WikibaseHelper(sparql_endpoint_url)

        self.statements = None

    def make_statements(self):
        s = []
        helper = self.helper
        # instance of edition
        s.append(wdi_core.WDItemID(helper.get_qid('Q3331189'), helper.get_pid("P31")))
        # edition or translation of
        s.append(wdi_core.WDItemID(self.edition_of_qid, helper.get_pid("P629")))
        # edition number
        s.append(wdi_core.WDString(self.edition, helper.get_pid("P393")))

        if self.archive_url:
            s.append(wdi_core.WDUrl(self.archive_url, helper.get_pid('P1065')))

        if self.pub_date:
            s.append(wdi_core.WDTime(self.pub_date, helper.get_pid('P577'), precision=self.date_precision))

        self.statements = s

    def get_or_create(self, login=None):

        # check in cache
        key = (self.sparql_endpoint_url, self.edition_of_qid, self.edition)
        if key in self._release_cache:
            return self._release_cache[key]

        # check in wikidata
        # edition number, filter by edition of and instance of edition
        helper = self.helper
        edition_dict = id_mapper(helper.get_pid("P393"),
                                 ((helper.get_pid("P629"), self.edition_of_qid),
                                  (helper.get_pid("P31"), helper.get_qid("Q3331189"))),
                                 endpoint=self.sparql_endpoint_url)
        if edition_dict and self.edition in edition_dict:
            # add to cache
            self._release_cache[key] = edition_dict[self.edition]
            return edition_dict[self.edition]

        # create new
        if login is None:
            raise ValueError("login required to create item")

        self.make_statements()
        item = wdi_core.WDItemEngine(item_name=self.title, data=self.statements, domain="release",
                                     mediawiki_api_url=self.mediawiki_api_url,
                                     sparql_endpoint_url=self.sparql_endpoint_url)
        item.set_label(self.title)
        item.set_description(description=self.description, lang='en')
        write_success = try_write(item, self.edition + "|" + self.edition_of_qid, 'P393|P629', login)
        if write_success:
            # add to cache
            self._release_cache[key] = item.wd_item_id
            return item.wd_item_id
        else:
            raise write_success

    def get_all_releases(self):
        # helper function to get all releases for the edition_of_qid given
        helper = self.helper
        edition_dict = id_mapper(helper.get_pid("P393"),
                                 ((helper.get_pid("P629"), self.edition_of_qid),
                                  (helper.get_pid("P31"), helper.get_qid("Q3331189"))),
                                 endpoint=self.sparql_endpoint_url)
        return edition_dict


class Publication:
    # https://github.com/shexSpec/schemas/blob/master/Wikidata/wikicite/wikicite_scholarly_article.shex

    ID_TYPES = {
        "doi": "P356",
        "pmid": "P698",
        "pmcid": "P932"
    }

    INSTANCE_OF = {
        "scientific_article": "Q13442814",
        "publication": "Q732577"
    }

    SOURCES = {
        'crossref': 'Q5188229',
        'europepmc': 'Q5412157'
    }

    def __init__(self, title=None, instance_of=None, subtitle=None, authors=None,
                 publication_date=None, original_language_of_work=None,
                 published_in_issn=None, published_in_isbn=None,
                 volume=None, issue=None, pages=None, number_of_pages=None, cites=None,
                 editor=None, license=None, full_work_available_at=None, language_of_work_or_name=None,
                 main_subject=None, commons_category=None, sponsor=None, data_available_at=None,
                 ids=None, ref_url=None, source=None):
        """

        :param title:
        :type title: str
        :param instance_of: one of `INSTANCE_OF`
        :type instance_of: str
        :param authors: authors is a list of dicts, containing the following keys: full_name, orcid (optional)
                example: {'full_name': "Andrew I. Su", 'orcid': "0000-0002-9859-4104"}
                If author name can't be parsed, use value None. i.e. {'full_name': None}
        :type authors: list
        :param publication_date:
        :type publication_date: datetime.datetime
        :param published_in_issn: The issn# for the journal
        :type published_in_issn: str
        :param published_in_isbn: The isbn#
        :type published_in_isbn: str
        :param volume:
        :type volume: str
        :param issue:
        :type issue: str
        :param pages:
        :type pages: str
        :param ids: may contain the following keys: doi, pmid, pmcid, article_id, arxiv_id, bibcode, zoobank_pub_id,
        jstor_article_id, ssrn_id, nioshtic2_id, dialnet_article, opencitations_id, acmdl_id, publons_id
        example: {'doi': 'xxx', 'pmid': '1234'}
        :type ids: dict
        :param ref_url: Ref url (for the api call)
        :type ref_url: str
        :param source: One of {'crossref', 'europepmc'}
        :type source: str
        :param subtitle: Not implemented
        :param original_language_of_work: Not implemented
        :param number_of_pages: Not implemented
        :param cites: Not implemented
        :param editor: Not implemented
        :param license: Not implemented
        :param full_work_available_at: Not implemented
        :param language_of_work_or_name: Not implemented
        :param main_subject: Not implemented
        :param commons_category: Not implemented
        :param sponsor: Not implemented
        :param data_available_at: Not implemented
        """
        # Input is an API agnostic representation of a publication
        self.warnings = []
        self._instance_of = instance_of
        self.instance_of_qid = None
        self._published_in_isbn = published_in_isbn
        self._published_in_issn = published_in_issn
        self.published_in_qid = None
        self._authors = authors
        self.title = title
        self.publication_date = publication_date
        self.volume = volume
        self.issue = issue
        self.pages = pages
        self.ids = ids
        self.source = source
        self.ref_url = ref_url

        ### not implemented ###
        self.subtitle = subtitle
        self.original_language_of_work = original_language_of_work
        self.cites = cites
        self.editor = editor
        self.license = license
        self.full_work_available_at = full_work_available_at
        self.language_of_work_or_name = language_of_work_or_name
        self.main_subject = main_subject
        self.commons_category = commons_category
        self.sponsor = sponsor
        self.data_available_at = data_available_at
        self.number_of_pages = number_of_pages

        ### wikidata related things ###
        self.reference = None
        self.statements = []

    @property
    def instance_of(self):
        return self._instance_of

    @instance_of.setter
    def instance_of(self, value):
        self._instance_of = value
        self.instance_of_qid = self.INSTANCE_OF.get(value) if value in self.INSTANCE_OF else self.INSTANCE_OF[
            'publication']
        if value not in self.INSTANCE_OF:
            self.warnings.append("instance of {} not found".format(value))

    @property
    def published_in_issn(self):
        return self._published_in_issn

    @published_in_issn.setter
    def published_in_issn(self, value):
        # todo: handle multiple issn and isbn #s
        # right now: expect only one issn#
        self._published_in_issn = value
        self.published_in_qid = prop2qid(PROPS['ISSN'], value)
        if not self.published_in_qid:
            self.warnings.append("ISSN:{} not found".format(value))

    @property
    def published_in_isbn(self):
        return self._published_in_isbn

    @published_in_isbn.setter
    def published_in_isbn(self, value):
        # todo: handle multiple issn and isbn #s
        # right now: expect only one issn#
        self._published_in_isbn = value
        self.published_in_qid = prop2qid(PROPS['ISBN'], value)
        # todo: check to see if isbn and issn numbers are conflicting
        if not self.published_in_qid:
            self.warnings.append("ISBN:{} not found".format(value))

    @property
    def authors(self):
        return self._authors

    @authors.setter
    def authors(self, value):
        self._authors = value
        for author in self._authors:
            author['qid'] = Publication.lookup_author(author['orcid']) if 'orcid' in author else None

    @staticmethod
    def lookup_author(orcid_id):
        return prop2qid(PROPS['orcid id'], orcid_id)

    def validate(self):
        assert self.title is not None and len(self.title) > 1
        assert self.publication_date is None or isinstance(self.publication_date, datetime.datetime)
        assert self.source in self.SOURCES
        assert self.ref_url is not None and len(self.ref_url) > 1

    def make_reference(self):
        if self.source == "crossref":
            extid = wdi_core.WDString(self.ids['doi'], PROPS['DOI'], is_reference=True)
            ref_url = wdi_core.WDUrl(self.ref_url, PROPS['reference URL'], is_reference=True)
            stated_in = wdi_core.WDItemID(self.SOURCES[self.source], PROPS['stated in'], is_reference=True)
            retrieved = wdi_core.WDTime(strftime("+%Y-%m-%dT00:00:00Z", gmtime()), PROPS['retrieved'],
                                        is_reference=True)
            self.reference = [stated_in, extid, ref_url, retrieved]
        elif self.source == "europepmc":
            # do stuff here
            pass

    def set_label(self, item):
        # item is a WDItemEngine
        # check if lenght is > 250, warn if so and truncate
        # self.title
        if item.get_label() == "":
            if len(self.title) > 249:
                self.warnings.append("title cropped to 250 chars")
            item.set_label(self.title[:249])

    def set_description(self, item):
        # item is a WDItemEngine
        if item.get_description() == "" and self.publication_date:
            item.set_description("{} published on {}".format(self.instance_of.replace("_", " "),
                                                             self.publication_date.strftime("%d %B %Y")))
        elif item.get_description() == "":
            item.set_description("{}".format(self.instance_of.replace("_", " ")))

    def make_statements(self):
        self.statements.append(
            wdi_core.WDItemID(self.instance_of_qid, PROPS['instance of'], references=[self.reference]))
        self.statements.append(wdi_core.WDMonolingualText(self.title, PROPS['title'], references=[self.reference]))

        if self.publication_date:
            date = self.publication_date.strftime("+%Y-%m-%dT00:00:00Z")
            self.statements.append(
                wdi_core.WDTime(date, PROPS['publication date'], references=[self.reference]))
        if self.published_in_qid:
            self.statements.append(
                wdi_core.WDItemID(self.published_in_qid, PROPS['published in'], references=[self.reference]))
        if self.volume:
            self.statements.append(wdi_core.WDString(self.volume, PROPS['volume'], references=[self.reference]))
        if self.pages:
            self.statements.append(wdi_core.WDString(self.pages, PROPS['page(s)'], references=[self.reference]))
        if self.issue:
            self.statements.append(wdi_core.WDString(self.issue, PROPS['issue'], references=[self.reference]))

    def make_author_statements(self):
        # this function exists separately because if the item already exists, we don't want to touch the authors
        s = []
        for n, author in enumerate(self.authors, 1):
            series_ordinal = wdi_core.WDString(str(n), PROPS['series ordinal'], is_qualifier=True)
            if author.get("qid"):
                s.append(wdi_core.WDItemID(author['qid'], PROPS['author'],
                                           references=[self.reference], qualifiers=[series_ordinal]))
            elif author['full_name']:
                s.append(wdi_core.WDString(author['full_name'], PROPS['author name string'],
                                           references=[self.reference], qualifiers=[series_ordinal]))
        self.statements.extend(s)

    def make_ext_id_statements(self):
        for id_type, id_value in self.ids.items():
            self.statements.append(wdi_core.WDExternalID(id_value, self.ID_TYPES[id_type], references=[self.reference]))

    def get_or_create(self, login):
        self.validate()
        self.make_reference()
        self.make_statements()
        self.make_ext_id_statements()

        item = wdi_core.WDItemEngine(
            item_name=self.title, data=self.statements,
            domain="scientific_article",
            append_value=[PROPS['DOI'], PROPS['PMCID'], PROPS['PubMed ID']],
            # ref_handler=update_retrieved_if_new_multiple_refs()
        )

        if item.wd_item_id:
            return item.wd_item_id, self.warnings, ""

        self.set_label(item)
        self.set_description(item)

        if item.create_new_item:
            self.make_author_statements()

        success = try_write(item, self.ids['doi'], PROPS["DOI"], login)
        if success is not True:
            return item.wd_item_id, self.warnings, success
        else:
            return item.wd_item_id, self.warnings, ""


def crossref_api_to_publication(ext_id, id_type="doi"):
    assert id_type == "doi"
    url = "https://api.crossref.org/v1/works/http://dx.doi.org/{}"
    url = url.format(ext_id)

    response = requests.get(url)
    response.raise_for_status()
    r = response.json()

    assert r['status'] == 'ok'
    r = r['message']

    p = Publication(source="crossref", ref_url=url)
    if r['type'] == "journal-article":
        p.instance_of = "scientific_article"
    else:
        p.warnings.append("unknown type: {}".format(r['type']))

    p.title = r['title'][0]
    p.published_in_issn = r.get('ISSN', [None])[0]
    p.publication_date = datetime.datetime.fromtimestamp(int(r['created']['timestamp']) / 1000)
    p.issue = r.get('issue')
    p.volume = r.get('volume')
    p.pages = r.get('page')
    p.authors = [{'full_name': x['given'] + " " + x['family'],
                  'orcid': x.get("ORCID", "").replace("http://orcid.org/", "")} for x in r['author']]

    p.ids = {'doi': ext_id}

    return p


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


def prop2qid(prop, value, endpoint='https://query.wikidata.org/sparql'):
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
    results = WDItemEngine.execute_sparql_query(query, endpoint=endpoint)
    result = results['results']['bindings']
    if len(result) == 0:
        # not found
        return None
    elif len(result) > 1:
        raise ValueError("More than one wikidata ID found for {} {}: {}".format(prop, value, result))
    else:
        return result[0]['item']['value'].split("/")[-1]


def id_mapper(prop, filters=None, raise_on_duplicate=False, return_as_set=False, prefer_exact_match=False,
              endpoint='https://query.wikidata.org/sparql'):
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
    results = WDItemEngine.execute_sparql_query(query, endpoint=endpoint)['results']['bindings']
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
    dupe = {k: v for k, v in id_qid.items() if len(v) > 1}
    if raise_on_duplicate and dupe:
        raise ValueError("duplicate ids: {}".format(dupe))

    if return_as_set:
        return dict(id_qid)
    else:
        return {x['id']: x['item'] for x in results}


def get_last_modified_header(entity="http://www.wikidata.org", endpoint='https://query.wikidata.org/sparql'):
    # this will work on wikidata or any particular entity
    query = "select ?d where {{<{}> schema:dateModified ?d}}".format(entity)
    results = WDItemEngine.execute_sparql_query(query, endpoint=endpoint)['results']['bindings']
    results = [{k: v['value'] for k, v in x.items()} for x in results]
    t = results[0]['d']
    try:
        # wikidata format
        dt = datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        # wikibase format
        dt = datetime.datetime.strptime(t, '%Y-%m-%dT%H:%M:%S.%fZ')
    return dt


def wait_for_last_modified(timestamp, delay=30, entity="http://www.wikidata.org",
                           endpoint='https://query.wikidata.org/sparql'):
    # wait until the last modified timestamp is newer than `timestamp`
    assert isinstance(timestamp, datetime.datetime)
    t = tqdm(desc="Waiting for endpoint update:  / {} ".format(timestamp))
    while True:
        last_modified_header = get_last_modified_header(entity=entity, endpoint=endpoint)
        t.set_description("Waiting for endpoint update: {} / {} ".format(last_modified_header, timestamp))
        t.update(1)
        if last_modified_header >= timestamp:
            break
        sleep(delay)

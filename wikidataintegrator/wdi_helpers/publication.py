from time import gmtime, strftime, sleep
import datetime
import difflib
import argparse
import sys
import os
import requests
from dateutil import parser as du

from .. import wdi_core, wdi_login
from wikidataintegrator.wdi_config import config
from wikidataintegrator.wdi_helpers import prop2qid, PROPS, try_write


class PubmedItem:
    def __init__(self):
        raise ValueError("PubmedItem is deprecated. Please use PublicationHelper")


class Publication:
    # https://github.com/shexSpec/schemas/blob/master/Wikidata/wikicite/wikicite_scholarly_article.shex

    ID_TYPES = {
        "doi": "P356",
        "pmid": "P698",
        "pmcid": "P932",
        'arxiv': 'P818',
        'biorxiv': 'P3951',
    }

    INSTANCE_OF = {
        "scientific_article": "Q13442814",
        "publication": "Q732577",
        'preprint': 'Q580922',
    }

    SOURCES = {
        'crossref': 'Q5188229',
        'europepmc': 'Q5412157',
        'arxiv': 'Q118398',
        'biorxiv': 'Q19835482',
        'chemrxiv': 'Q50012382',
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
        :type authors: Optional[list]
        :param publication_date:
        :type publication_date: datetime.datetime
        :param published_in_issn: The issn# for the journal
        :type published_in_issn: str or list
        :param published_in_isbn: The isbn#
        :type published_in_isbn: str or list
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
        if authors is None:
            authors = []

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
        assert self.published_in_isbn is None, "Can't give both ISSN and ISBN"
        if not isinstance(value, list):
            value = [value]
        self._published_in_issn = value
        qids = set(prop2qid(PROPS['ISSN'], v) for v in value)
        if len(qids) == 1:
            self.published_in_qid = list(qids)[0]
        else:
            self.warnings.append("conflictings ISSN qids: {}".format(qids))
        if not self.published_in_qid:
            self.warnings.append("ISSN:{} not found".format(value))

    @property
    def published_in_isbn(self):
        return self._published_in_isbn

    @published_in_isbn.setter
    def published_in_isbn(self, value):
        assert self.published_in_issn is None, "Can't give both ISSN and ISBN"
        if not isinstance(value, list):
            value = [value]
        self._published_in_isbn = value
        qids = set(prop2qid(PROPS['ISBN-13'], v) for v in value)
        if len(qids) == 1:
            self.published_in_qid = list(qids)[0]
        else:
            self.warnings.append("conflictings ISBN qids: {}".format(qids))
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
            assert 'doi' in self.ids
            edt_id_id, ext_id_prop = self.ids['doi'], PROPS['DOI']
        elif self.source == "europepmc":
            assert 'pmcid' in self.ids
            edt_id_id, ext_id_prop = self.ids['pmcid'], PROPS['PMCID']
        elif self.source == 'arxiv':
            assert 'arxiv' in self.ids
            edt_id_id, ext_id_prop = self.ids['arxiv'], PROPS['arxiv id']
        elif self.source == 'biorxiv':
            edt_id_id, ext_id_prop = self.ids['biorxiv'], self.ID_TYPES['biorxiv']
        elif self.source == 'chemrxiv':
            edt_id_id, ext_id_prop = self.ids['doi'], self.ID_TYPES['doi']
        else:
            raise ValueError(f'Unhandled source: {self.source}')

        extid = wdi_core.WDString(edt_id_id, ext_id_prop, is_reference=True)
        ref_url = wdi_core.WDUrl(self.ref_url, PROPS['reference URL'], is_reference=True)
        stated_in = wdi_core.WDItemID(self.SOURCES[self.source], PROPS['stated in'], is_reference=True)
        retrieved = wdi_core.WDTime(strftime("+%Y-%m-%dT00:00:00Z", gmtime()), PROPS['retrieved'],
                                    is_reference=True)
        self.reference = [stated_in, extid, ref_url, retrieved]

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
        if self.instance_of_qid is None:
            raise ValueError('can not create WDItemID with None')
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
            if id_value:
                id_value = id_value.upper()
                self.statements.append(wdi_core.WDExternalID(id_value, self.ID_TYPES[id_type], references=[self.reference]))

    def get_or_create(self, login):
        self.validate()
        self.make_reference()
        self.make_statements()
        self.make_ext_id_statements()
        self.make_author_statements()

        item = wdi_core.WDItemEngine(
            data=self.statements,
            append_value=[PROPS['DOI'], PROPS['PMCID'], PROPS['PubMed ID']],
            # ref_handler=update_retrieved_if_new_multiple_refs()
        )

        if item.wd_item_id:
            return item.wd_item_id, self.warnings, True

        self.set_label(item)
        self.set_description(item)

        if self.source == 'arxiv':
            success = try_write(item, self.ids['arxiv'], PROPS["arxiv id"], login)
        elif self.source == 'biorxiv':
            success = try_write(item, self.ids['biorxiv'], PROPS["biorxiv id"], login)
        else:
            success = try_write(item, self.ids['doi'], PROPS["DOI"], login)
        return item.wd_item_id, self.warnings, success


def crossref_api_to_publication(ext_id, id_type="doi"):
    assert id_type == "doi", "Unsupported id type in crossref: {}".format(id_type)
    url = "https://api.crossref.org/v1/works/https://doi.org/{}"
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
    if 'author' in r:
        p.authors = [{'full_name': x['given'] + " " + x['family'],
                      'orcid': x.get("ORCID", "").replace("http://orcid.org/", "")} for x in r['author']]

    p.ids = {'doi': ext_id}

    return p

def opencitations_api_to_publication(ext_id, id_type="doi"):
    assert id_type == "doi", "Unsupported id type in OpenCitations: {}".format(id_type)
    url = "https://w3id.org/oc/index/api/v1/metadata/{}"
    url = url.format(ext_id)

    response = requests.get(url)
    response.raise_for_status()
    r = response.json()

    assert r['status'] == 'ok'
    r = r['message']

    p = Publication(source="opencitations", ref_url=url)
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
    if 'author' in r:
        p.authors = [{'full_name': x['given'] + " " + x['family'],
                      'orcid': x.get("ORCID", "").replace("http://orcid.org/", "")} for x in r['author']]

    p.ids = {'doi': ext_id}

    return p


def europepmc_api_to_publication(ext_id, id_type):
    # https://europepmc.org/docs/EBI_Europe_PMC_Web_Service_Reference.pdf
    assert id_type in Publication.ID_TYPES, "id_type must be in {}".format(Publication.ID_TYPES.keys())
    # Request the data
    if id_type == "pmcid":
        url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=PMCID:PMC{}&resulttype=core&format=json'
        url = url.format(ext_id)
    elif id_type == "doi":
        url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=DOI:%22{}%22&resulttype=core&format=json"
        url = url.format(ext_id)
    elif id_type == "pmid":
        url = 'https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:{}%20AND%20SRC:MED&resulttype=core&format=json'
        url = url.format(ext_id, id_type)
    else:
        raise ValueError("id_type must be in {}".format(Publication.ID_TYPES.keys()))
    headers = {
        'User-Agent': config['USER_AGENT_DEFAULT']
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    d = response.json()
    if d['hitCount'] != 1:
        raise ValueError("No results")
    article = d['resultList']['result'][0]

    p = Publication()
    p.ref_url = url
    p.source = "europepmc"
    original_title = article['title']
    # to remove trailing dot
    # to exclude '...' and abbreviations such as U.S.A.
    p.title = original_title
    if original_title[-1] == '.' and original_title[-3] != '.':
        p.title = original_title[:-1]  # drop the trailing dot

    authors = []
    authorlist = article["authorList"]["author"]
    for author in authorlist:
        full_name = None
        if 'firstName' in author and 'lastName' in author:
            full_name = author['firstName'] + ' ' + author['lastName']
        elif 'fullName' in author:
            full_name = author['fullName']
        elif 'collectiveName' in author:
            full_name = author['collectiveName']
        else:
            msg = "unknown author: {}".format(author)
            p.warnings.append(msg)
        # orcids
        orcid = None
        if 'authorId' in author:
            if author['authorId']['type'] == "ORCID":
                orcid = author['authorId']['value']
        authors.append({'full_name': full_name, 'orcid': orcid})
    p.authors = authors
    p.publication_date = du.parse(article['firstPublicationDate'])
    p.volume = article['journalInfo'].get('volume')
    p.issue = article['journalInfo'].get('issue')
    p.pages = article.get('pageInfo')

    p.ids = dict()
    p.ids['doi'] = article.get('doi')
    p.ids['pmid'] = article.get('pmid')
    p.ids['pmcid'] = article.get('pmcid', '').replace("PMC", "")

    if 'pageInfo' in article:
        # according to documentation, they should be in the form : 145-178, but also "D36-42" has been in the responses
        try:
            pageString = article['pageInfo']
            pageStringParts = pageString.split('-')
            pageStartString = pageStringParts[0]
            if pageStartString.startswith('D'):
                pageStartString = pageStartString[1:]
            pageStart = int(pageStartString)
            pageEndString = pageStringParts[1]
            pageEnd = int(pageEndString)
            pages = pageEnd - pageStart + 1
            p.number_of_pages = pages
        except Exception:
            pass
    """
    # this is probably a list, and we need to be able to look up a qid from "NCI NIH HHS" for example...
    if "grantsList" in article and "grant" in article['grantsList'] and "agency" in article['grantsList']["grant"]:
        p.sponsor = article['grantsList']["grant"]["agency"]
    """

    # get the type of publication
    # if not told that it is a research-article, we will make it a general publication
    isScientificArticle = False
    if 'pubTypeList' in article:
        pubtypes = article['pubTypeList']['pubType']
        if isinstance(pubtypes, str):
            if pubtypes == 'research-article':
                isScientificArticle = True
        elif isinstance(pubtypes, list):
            if 'research-article' in pubtypes:
                isScientificArticle = True
    if isScientificArticle:
        p.instance_of = "scientific_article"
    else:
        p.instance_of = "publication"
        p.warnings.append("unknown publication type, assuming publication")

    issns = []
    if 'issn' in article['journalInfo']['journal']:
        issns.append(article['journalInfo']['journal']['issn'])
    elif 'essn' in article['journalInfo']['journal']:
        issns.append(article['journalInfo']['journal']['essn'])
    else:
        msg = "unknown journal: {}".format(article['journalInfo']['journal'])
        p.warnings.append(msg)
    p.published_in_issn = issns

    return p



def arxiv_api_to_publication(ext_id, id_type='arxiv'):
    """Make a Publication from an arXiv identifier."""
    from manubot.cite.arxiv import get_arxiv_csl_item
    j = get_arxiv_csl_item(ext_id)

    year, month, day = j['issued']['date-parts'][0]

    publication = Publication(
        title=j['title'],
        ref_url=j['URL'],
        authors=[
            {
                'full_name': f'{author["given"]} {author["family"]}',
            }
            for author in j['author']
        ],
        publication_date=datetime.datetime(year=year, month=month, day=day),
        ids={'arxiv': ext_id},
        source='arxiv',
        full_work_available_at=f'https://arxiv.org/pdf/{ext_id}',
    )
    publication.instance_of = 'preprint'
    publication.published_in_qid = Publication.SOURCES['arxiv']
    return publication


def biorxiv_api_to_publication(biorxiv_id: str, id_type='biorxiv') -> Publication:
    """Make a :class:`Publication` from a bioRxiv identifier."""
    url = f'https://api.biorxiv.org/details/biorxiv/10.1101/{biorxiv_id}'
    headers = {
        'User-Agent': config['USER_AGENT_DEFAULT']
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    revisions = response.json()['collection']
    latest_revision = revisions[-1]
    version = latest_revision['version']
    authors = [author.strip() for author in latest_revision['authors'].split(';')]

    publication = Publication(
        title=latest_revision['title'],
        ref_url=f'https://www.biorxiv.org/content/10.1101/{biorxiv_id}v{version}',
        authors=[
            {
                'full_name': author,
            }
            for author in authors
            if author
        ],
        publication_date=datetime.datetime.strptime(latest_revision['date'], '%Y-%m-%d'),
        ids={
            'biorxiv': biorxiv_id,
            'doi': latest_revision['doi'],
        },
        source='biorxiv',
        full_work_available_at=f'https://www.biorxiv.org/content/10.1101/{biorxiv_id}v{version}.full.pdf',
    )
    publication.instance_of = 'preprint'
    publication.published_in_qid = Publication.SOURCES['biorxiv']
    return publication


def chemrxiv_api_to_publication(chemrxiv_id: str, id_type='chemrxiv') -> Publication:
    """Make a :class:`Publication` from a ChemRxiv identifier."""
    url = f'https://api.figshare.com/v2/articles/{chemrxiv_id}'
    headers = {
        'User-Agent': config['USER_AGENT_DEFAULT']
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    res_json = res.json()

    publication = Publication(
        title=res_json['title'],
        ref_url=res_json['figshare_url'],
        authors=[
            {
                'full_name': author['full_name'],
                'orcid': author.get('orcid_id'),
            }
            for author in res_json['authors']
        ],
        publication_date=datetime.datetime.strptime(res_json['published_date'], '%Y-%m-%dT%H:%M:%SZ'),
        ids={
            'doi': res_json['doi'],
        },
        source='chemrxiv',
    )
    publication.instance_of = 'preprint'
    publication.published_in_qid = Publication.SOURCES['chemrxiv']
    return publication


class PublicationHelper:
    SOURCE_FUNCT = {
        'crossref': crossref_api_to_publication,
        'europepmc': europepmc_api_to_publication,
        'arxiv': arxiv_api_to_publication,
        'biorxiv': biorxiv_api_to_publication,
        'chemrxiv': chemrxiv_api_to_publication,
    }

    def __init__(self, ext_id, id_type, source):
        """
        PublicationHelper: Helper to create wikidata items about literature
        Supported data sources and (ID types): crossref (doi), europepmc (pmid, pmcid, doi)

        :param ext_id: the external ID to use
        :type ext_id: str
        :param id_type: one of {'pmid', 'pmcid', 'doi'}
        :type id_type: str
        :param source: one of {'crossref', 'europepmc'}
        :type source: str
        """
        assert source in self.SOURCE_FUNCT
        self.f = self.SOURCE_FUNCT[source]
        self.e = None
        try:
            self.p = self.f(ext_id, id_type=id_type)
        except Exception as e:
            self.p = None
            self.e = e

    def get_or_create(self, login):
        """
        Get the qid of the item by its external id or create if doesn't exist

        :param login: WDLogin item
        :return: tuple of (qid, list of warnings (strings), success (True if success, returns the Exception otherwise))
        """
        if self.p:
            try:
                return self.p.get_or_create(login)
            except Exception as e:
                return None, self.p.warnings, e
        else:
            return None, [], self.e


def main():
    try:
        from local import WDUSER, WDPASS
    except ImportError:
        if "WDUSER" in os.environ and "WDPASS" in os.environ:
            WDUSER = os.environ['WDUSER']
            WDPASS = os.environ['WDPASS']
        else:
            import getpass
            WDUSER = input('Wikidata Username: ')
            WDPASS = getpass.getpass('Wikidata Password: ')

    parser = argparse.ArgumentParser(description='run publication creator')
    parser.add_argument("ext_id", help="comma-separated list of IDs")
    parser.add_argument("--source", help="API to use (crossref or europepmc)", default="crossref")
    parser.add_argument("--idtype", help="external id type (doi, pmcid, pmid, etc...)", default="doi")
    args = parser.parse_args()

    login = wdi_login.WDLogin(WDUSER, WDPASS)

    ext_ids = sorted(list(set(map(str.strip, args.ext_id.split(",")))))
    id_type = args.idtype
    source = args.source

    with open("log.txt", "a") as f:
        for ext_id in ext_ids:
            try:
                p = PublicationHelper(ext_id, id_type=id_type, source=source)
                qid, warnings, success = p.get_or_create(login)
                print("{},{},{},{}".format(ext_id, qid, "|".join(warnings), success))
                print("{},{},{},{}".format(ext_id, qid, "|".join(warnings), success), file=f)
                sleep(3)
            except Exception as e:
                print("{},{},{},{}".format(ext_id, None, e, False))
                print("{},{},{},{}".format(ext_id, None, e, False), file=f)


if __name__ == "__main__":
    main()

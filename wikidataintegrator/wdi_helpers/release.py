import datetime

from wikidataintegrator import wdi_core
from wikidataintegrator.wdi_helpers import id_mapper, try_write
from wikidataintegrator.wdi_helpers.wikibase_helper import WikibaseHelper


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
        item = wdi_core.WDItemEngine(data=self.statements,
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

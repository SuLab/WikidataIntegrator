import copy
import pprint
import unittest

import requests

from wikidataintegrator import wdi_core, wdi_fastrun
from wikidataintegrator.wdi_core import WDApiError

__author__ = 'Sebastian Burgstaller-Muehlbacher'
__license__ = 'AGPLv3'


class TestMediawikiApiCall(unittest.TestCase):
    def test_all(self):
        with self.assertRaises(WDApiError):
            wdi_core.WDItemEngine.mediawiki_api_call("GET", "http://www.wikidataaaaaaaaa.org",
                                                     max_retries=3, retry_after=1,
                                                     params={'format': 'json', 'action': 'wbgetentities', 'ids': 'Q42'})
        with self.assertRaises(requests.HTTPError):
            wdi_core.WDItemEngine.mediawiki_api_call("GET", "http://httpstat.us/400", max_retries=3, retry_after=1)

        wdi_core.WDItemEngine.mediawiki_api_call("GET", max_retries=3, retry_after=1,
                                                 params={'format': 'json', 'action': 'wbgetentities', 'ids': 'Q42'})


class TestDataType(unittest.TestCase):
    def test_wd_quantity(self):
        dt = wdi_core.WDQuantity(value='34', prop_nr='P43')

        dt_json = dt.get_json_representation()

        if not dt_json['mainsnak']['datatype'] == 'quantity':
            raise

        value = dt_json['mainsnak']['datavalue']

        if not value['value']['amount'] == '+34':
            raise

        if not value['value']['unit'] == '1':
            raise

        dt2 = wdi_core.WDQuantity(value='34', prop_nr='P43', upper_bound='35', lower_bound='33')

        value = dt2.get_json_representation()['mainsnak']['datavalue']

        if not value['value']['amount'] == '+34':
            raise

        if not value['value']['unit'] == '1':
            raise

        if not value['value']['upperBound'] == '+35':
            raise

        if not value['value']['lowerBound'] == '+33':
            raise

    def test_wd_geoshape(self):
        dt = wdi_core.WDGeoShape(value='Data:Inner_West_Light_Rail_stops.map', prop_nr='P43')

        dt_json = dt.get_json_representation()

        if not dt_json['mainsnak']['datatype'] == 'geo-shape':
            raise

        value = dt_json['mainsnak']['datavalue']

        if not value['value'] == 'Data:Inner_West_Light_Rail_stops.map':
            raise

        if not value['type'] == 'string':
            raise

    def test_wd_string(self):
        pass

    def test_live_item(self):
        wd_item = wdi_core.WDItemEngine(wd_item_id='Q423111')

        mass_statement = [x for x in wd_item.statements if x.get_prop_nr() == 'P2067'].pop()
        pprint.pprint(mass_statement.get_json_representation())

        if not mass_statement:
            raise

            # TODO: get json directly from the API and compare part to WDItemEngine


class TestFastRun(unittest.TestCase):
    """
    some basic tests for fastrun mode
    
    """

    def test_fast_run(self):
        qid = 'Q27552312'

        statements = [
            wdi_core.WDExternalID(value='P40095', prop_nr='P352'),
            wdi_core.WDExternalID(value='YER158C', prop_nr='P705')
        ]

        frc = wdi_fastrun.FastRunContainer(base_filter={'P352': '', 'P703': 'Q27510868'},
                                           base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)

        fast_run_result = frc.write_required(data=statements)

        if fast_run_result:
            message = 'fastrun failed'
        else:
            message = 'successful fastrun'
        print(fast_run_result, message)

        # here, fastrun should succeed, if not, test failed
        # if fast_run_result:
        #    raise ValueError

    def test_fastrun_label(self):
        # tests fastrun label, description and aliases, and label in another language
        data = [wdi_core.WDExternalID('/m/02j71', 'P646')]
        fast_run_base_filter = {'P361': 'Q18589965'}
        item = wdi_core.WDItemEngine(wd_item_id="Q2", data=data, fast_run=True,
                                     fast_run_base_filter=fast_run_base_filter)

        frc = wdi_core.WDItemEngine.fast_run_store[0]
        frc.debug = True

        assert item.get_label('en') == "Earth"
        descr = item.get_description('en')
        assert len(descr) > 3
        aliases = item.get_aliases()
        assert "Terra" in aliases

        assert list(item.fast_run_container.get_language_data("Q2", 'en', 'label'))[0] == "Earth"
        assert item.fast_run_container.check_language_data("Q2", ['not the Earth'], 'en', 'label')
        assert "Terra" in item.get_aliases()
        assert "planet" in item.get_description()

        assert item.get_label("es") == "Tierra"

        item.set_description(descr)
        item.set_description("fghjkl")
        assert item.wd_json_representation['descriptions']['en'] == {'language': 'en', 'value': 'fghjkl'}
        item.set_label("Earth")
        item.set_label("xfgfdsg")
        assert item.wd_json_representation['labels']['en'] == {'language': 'en', 'value': 'xfgfdsg'}
        item.set_aliases(["fake alias"], append=True)
        assert {'language': 'en', 'value': 'fake alias'} in item.wd_json_representation['aliases']['en']

        # something thats empty (for now.., can change, so this just makes sure no exception is thrown)
        frc.check_language_data("Q2", ['Ewiase'], 'ak', 'label')
        frc.check_language_data("Q2", ['not Ewiase'], 'ak', 'label')
        frc.check_language_data("Q2", [''], 'ak', 'description')
        frc.check_language_data("Q2", [], 'ak', 'aliases')
        frc.check_language_data("Q2", ['sdf', 'sdd'], 'ak', 'aliases')

        item.get_label("ak")
        item.get_description("ak")
        item.get_aliases("ak")
        item.set_label("label", lang="ak")
        item.set_description("d", lang="ak")
        item.set_aliases(["a"], lang="ak", append=True)


def test_sitelinks():
    data = [wdi_core.WDItemID(value='Q12136', prop_nr='P31')]
    item = wdi_core.WDItemEngine(wd_item_id='Q622901', data=data)
    item.get_sitelink("enwiki")
    assert "enwiki" not in item.wd_json_representation['sitelinks']
    item.set_sitelink("enwiki", "something")
    assert item.get_sitelink("enwiki")['title'] == "something"
    assert "enwiki" in item.wd_json_representation['sitelinks']


def test_nositelinks():
    # this item doesn't and probably wont ever have any sitelinks (but who knows?? maybe one day..)
    data = [wdi_core.WDItemID(value='Q5', prop_nr='P31')]
    item = wdi_core.WDItemEngine(wd_item_id='Q27869338', data=data)
    item.get_sitelink("enwiki")
    assert "enwiki" not in item.wd_json_representation['sitelinks']
    item.set_sitelink("enwiki", "something")
    assert item.get_sitelink("enwiki")['title'] == "something"
    assert "enwiki" in item.wd_json_representation['sitelinks']


####
## tests for statement equality, with and without refs
####
def test_ref_equals():
    # statements are identical
    oldref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    olditem = wdi_core.WDItemID("Q123", "P123", references=[oldref])
    newitem = copy.deepcopy(olditem)
    assert olditem.equals(newitem, include_ref=False)
    assert olditem.equals(newitem, include_ref=True)

    # dates are a month apart
    newitem = copy.deepcopy(olditem)
    newitem.references[0][2] = wdi_core.WDTime('+2002-1-31T12:01:13Z', prop_nr='P813')
    assert olditem.equals(newitem, include_ref=False)
    assert not olditem.equals(newitem, include_ref=True)

    # multiple refs
    newitem = copy.deepcopy(olditem)
    newitem.references.append([wdi_core.WDExternalID(value='99999', prop_nr='P352')])
    assert olditem.equals(newitem, include_ref=False)
    assert not olditem.equals(newitem, include_ref=True)
    olditem.references.append([wdi_core.WDExternalID(value='99999', prop_nr='P352')])
    assert olditem.equals(newitem, include_ref=True)

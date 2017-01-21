import unittest
import pprint
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login

__author__ = 'Sebastian Burgstaller-Muehlbacher'
__license__ = 'AGPLv3'


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

    def test_wd_string(self):
        pass

    def test_live_item(self):
        wd_item = wdi_core.WDItemEngine(wd_item_id='Q423111')

        mass_statement = [x for x in wd_item.statements if x.get_prop_nr() == 'P2067'].pop()
        pprint.pprint(mass_statement.get_json_representation())

        if not mass_statement:
            raise

        # TODO: get json directly from the API and compare part to WDItemEngine

    def test_fast_run(self):
        qid = 'Q27552312'

        statements = [
            wdi_core.WDExternalID(value='P40095', prop_nr='P352'),
            wdi_core.WDExternalID(value='YER158C', prop_nr='P705')
        ]

        frc = wdi_fastrun.FastRunContainer(base_filter={'P352': '', 'P703': 'Q27510868'},
                                           base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)

        fast_run_result = frc.check_data(data=statements)

        if fast_run_result:
            message = 'fastrun failed'
        else:
            message = 'successful fastrun'
        print(fast_run_result, message)

        # here, fastrun should succeed, if not, test failed
        if fast_run_result:
            raise

    def test_deletion_request(self):
        items_for_deletion = ['Q423', 'Q43345']
        wdi_core.WDItemEngine.delete_items(item_list=items_for_deletion, reason='test deletion', login=None)


def test_fastrun_label():
    data = [wdi_core.WDItemID('Q544', 'P361')]
    fast_run_base_filter = {'P361': 'Q544'}
    item = wdi_core.WDItemEngine(wd_item_id="Q2", data=data, fast_run=True,
                                 fast_run_base_filter=fast_run_base_filter)
    assert item.get_label('en') == "Earth"
    assert item.fast_run_container.get_language_data("Q2", 'en', 'label')[0] == "Earth"
    assert item.fast_run_container.check_language_data("Q2", ['not the Earth'], 'en', 'label')
    assert "Terra" in item.get_aliases()

    """
    # this item has no aliases or a description, but it might change...
    data = [wdi_core.WDItemID('Q13442814', 'P31')]
    fast_run_base_filter = {'P1433': 'Q5227381'}
    item = wdi_core.WDItemEngine(wd_item_id="Q28445414", data=data, fast_run=True,
                                 fast_run_base_filter=fast_run_base_filter)
    """
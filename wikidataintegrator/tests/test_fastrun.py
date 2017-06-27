from functools import partial

from wikidataintegrator import wdi_core, wdi_fastrun
from wikidataintegrator.wdi_core import WDBaseDataType

wdi_fastrun.FastRunContainer.debug = True


def test_query_data():
    # This hits live wikidata and may change !!
    frc = wdi_fastrun.FastRunContainer(base_filter={'P699': ''},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    frc._query_data('P699')

    # https://www.wikidata.org/wiki/Q10874
    assert 'Q10874' in frc.prop_data
    assert 'P699' in frc.prop_data['Q10874']
    assert 'Q10874-7475555C-9EAB-45BB-B36B-C18AF5852FC8' in frc.prop_data['Q10874']['P699']
    d = frc.prop_data['Q10874']['P699']['Q10874-7475555C-9EAB-45BB-B36B-C18AF5852FC8']
    assert all(x in d for x in {'qual', 'ref', 'v'})
    assert frc.prop_data['Q10874']['P699']['Q10874-7475555C-9EAB-45BB-B36B-C18AF5852FC8']['v'] == 'DOID:1432'


def test_interpro_item_live():
    # This hits live wikidata and may change !!

    # dont check references. values are the same
    statements = [wdi_core.WDExternalID(value="IPR028732", prop_nr="P2926"),
                  wdi_core.WDItemID("Q24774044", "P279")]
    item = wdi_core.WDItemEngine(item_name="Matrix metalloproteinase-27", domain='interpro', data=statements,
                                 append_value=["P279", "P31"],
                                 fast_run=True, fast_run_base_filter={'P2926': '', 'P279': 'Q24774044'})
    assert item.require_write is False

    # check references, they are the same
    ref = [[wdi_core.WDItemID("Q29947749", "P248", is_reference=True),
            wdi_core.WDExternalID("IPR028732", "P2926", is_reference=True)]]
    statements = [wdi_core.WDExternalID(value="IPR028732", prop_nr="P2926", references=ref),
                  wdi_core.WDItemID("Q24774044", "P279", references=ref)]
    item = wdi_core.WDItemEngine(item_name="Matrix metalloproteinase-27", domain='interpro', data=statements,
                                 append_value=["P279", "P31"],
                                 fast_run=True, fast_run_base_filter={'P2926': '', 'P279': 'Q24774044'},
                                 fast_run_use_refs=True, ref_comparison_f=WDBaseDataType.custom_ref_equal_dates)
    assert item.require_write is False

    # check references, they are different
    ref = [[wdi_core.WDItemID("Q999999999", "P248", is_reference=True),
            wdi_core.WDExternalID("IPR028732", "P2926", is_reference=True)]]
    statements = [wdi_core.WDExternalID(value="IPR028732", prop_nr="P2926", references=ref),
                  wdi_core.WDItemID("Q24774044", "P279", references=ref)]
    item = wdi_core.WDItemEngine(item_name="Matrix metalloproteinase-27", domain='interpro', data=statements,
                                 append_value=["P279", "P31"],
                                 fast_run=True, fast_run_base_filter={'P2926': '', 'P279': 'Q24774044'},
                                 fast_run_use_refs=True, ref_comparison_f=WDBaseDataType.custom_ref_equal_dates)
    assert item.require_write


class frc_fake_query_data_ensembl(wdi_fastrun.FastRunContainer):
    def _query_data(self, prop_nr):
        self.prop_data['Q14911732'] = {'P594': {
            'fake statement id': {
                'qual': set(),
                'ref': {'fake ref id': {
                    ('P248', 'Q29458763'),  # stated in ensembl Release 88
                    ('P594', 'ENSG00000123374')}},
                'v': 'ENSG00000123374'}}}
        self.rev_lookup = {'ENSG00000123374': {'Q14911732'}}


class frc_fake_query_data_ensembl_no_ref(wdi_fastrun.FastRunContainer):
    def _query_data(self, prop_nr):
        self.prop_data['Q14911732'] = {'P594': {
            'fake statement id': {
                'qual': set(),
                'ref': dict(),
                'v': 'ENSG00000123374'}}}
        self.rev_lookup = {'ENSG00000123374': {'Q14911732'}}


def test_fastrun_ref_ensembl():
    # fastrun checks refs
    frc = frc_fake_query_data_ensembl(base_filter={'P594': '', 'P703': 'Q15978631'},
                                      base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                      use_refs=True)

    # statement has no ref
    statements = [wdi_core.WDExternalID(value='ENSG00000123374', prop_nr='P594')]
    assert frc.write_required(data=statements)

    # statement has the same ref
    statements = [wdi_core.WDExternalID(value='ENSG00000123374', prop_nr='P594',
                                        references=[[wdi_core.WDItemID("Q29458763", "P248", is_reference=True),
                                                     wdi_core.WDExternalID("ENSG00000123374", "P594",
                                                                           is_reference=True)]])]
    assert not frc.write_required(data=statements)

    # new statement has an different stated in
    statements = [wdi_core.WDExternalID(value='ENSG00000123374', prop_nr='P594',
                                        references=[[wdi_core.WDItemID("Q99999999999", "P248", is_reference=True),
                                                     wdi_core.WDExternalID("ENSG00000123374", "P594",
                                                                           is_reference=True)]])]
    assert frc.write_required(data=statements)

    # fastrun don't check references, statement has no reference,
    frc = frc_fake_query_data_ensembl_no_ref(base_filter={'P594': '', 'P703': 'Q15978631'},
                                             base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                             use_refs=False)
    statements = [wdi_core.WDExternalID(value='ENSG00000123374', prop_nr='P594')]
    assert not frc.write_required(data=statements)

    # fastrun don't check references, statement has reference,
    frc = frc_fake_query_data_ensembl_no_ref(base_filter={'P594': '', 'P703': 'Q15978631'},
                                             base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                             use_refs=False)
    statements = [wdi_core.WDExternalID(value='ENSG00000123374', prop_nr='P594',
                                        references=[[wdi_core.WDItemID("Q123", "P31", is_reference=True)]])]
    assert not frc.write_required(data=statements)


class frc_fake_query_data_doid(wdi_fastrun.FastRunContainer):
    #  https://www.wikidata.org/wiki/Q10874#P699
    def _query_data(self, prop_nr):
        self.prop_data['Q10874'] = {'P699': {
            'Q10874-7475555C-9EAB-45BB-B36B-C18AF5852FC8': {
                'qual': set(),
                'ref': {'04921d9e0eab8d4bbbf568fb4b06c4362d2ab57a': {
                    ('P248', 'Q28556593'),
                    ('P699', 'DOID:1432'),
                    ('P813', '+2017-01-31T00:00:00Z')}},
                'v': 'DOID:1432'}}}
        self.rev_lookup = {'DOID:1432': {'Q10874'}}


def test_fastrun_ref_doid():
    statement_no_ref = wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699')
    statement_diff_value_no_ref = wdi_core.WDExternalID(value='DOID:XXXX', prop_nr='P699')

    statement_current_ref = wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', references=[
        [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', is_reference=True),
         wdi_core.WDItemID(value='Q28556593', prop_nr='P248', is_reference=True),
         wdi_core.WDTime('+2017-01-31T00:00:00Z', prop_nr='P813', is_reference=True)]
    ])

    statement_no_retrieved = wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', references=[
        [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', is_reference=True),
         wdi_core.WDItemID(value='Q28556593', prop_nr='P248', is_reference=True)]
    ])

    statement_diff_stated_in = wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', references=[
        [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', is_reference=True),
         wdi_core.WDItemID(value='Q999999999', prop_nr='P248', is_reference=True),
         wdi_core.WDTime('+2017-01-31T00:00:00Z', prop_nr='P813', is_reference=True)]
    ])

    statement_10dayold_ref = wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', references=[
        [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', is_reference=True),
         wdi_core.WDItemID(value='Q28556593', prop_nr='P248', is_reference=True),
         wdi_core.WDTime('+2017-02-11T00:00:00Z', prop_nr='P813', is_reference=True)]
    ])

    statement_new_ref = wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', references=[
        [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', is_reference=True),
         wdi_core.WDItemID(value='Q28556593', prop_nr='P248', is_reference=True),
         wdi_core.WDTime('+2018-02-10T00:00:00Z', prop_nr='P813', is_reference=True)]
    ])

    # by default, don't check references, value is the same, so dont write
    frc = frc_fake_query_data_doid(base_filter={'P699': ''},
                                   base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    assert not frc.write_required(data=[statement_no_ref])
    assert frc.write_required(data=[statement_diff_value_no_ref])  # except this one
    assert not frc.write_required(data=[statement_current_ref])
    assert not frc.write_required(data=[statement_10dayold_ref])
    assert not frc.write_required(data=[statement_new_ref])
    assert not frc.write_required(data=[statement_no_retrieved])
    assert not frc.write_required(data=[statement_diff_stated_in])

    # check references
    frc = frc_fake_query_data_doid(base_filter={'P699': ''},
                                   base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                   use_refs=True)
    assert frc.write_required(data=[statement_no_ref])
    assert frc.write_required(data=[statement_diff_value_no_ref])
    assert not frc.write_required(data=[statement_current_ref])
    assert frc.write_required(data=[statement_10dayold_ref])
    assert frc.write_required(data=[statement_new_ref])
    assert frc.write_required(data=[statement_no_retrieved])
    assert frc.write_required(data=[statement_diff_stated_in])

    # check references with a custom function that checks the retrieved date
    frc = frc_fake_query_data_doid(base_filter={'P699': ''},
                                   base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                   use_refs=True, comparison_f=WDBaseDataType.custom_ref_equal_dates)
    assert frc.write_required(data=[statement_no_ref])
    assert frc.write_required(data=[statement_diff_value_no_ref])
    assert not frc.write_required(data=[statement_current_ref])
    assert not frc.write_required(data=[statement_10dayold_ref])
    assert frc.write_required(data=[statement_new_ref])
    assert frc.write_required(data=[statement_no_retrieved])
    assert frc.write_required(data=[statement_diff_stated_in])

    # check references with a custom function that checks the retrieved date, and lets 2 yr old reference go
    frc = frc_fake_query_data_doid(base_filter={'P699': ''},
                                   base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                   use_refs=True,
                                   comparison_f=partial(WDBaseDataType.custom_ref_equal_dates, days=2 * 365))
    assert frc.write_required(data=[statement_no_ref])
    assert frc.write_required(data=[statement_diff_value_no_ref])
    assert not frc.write_required(data=[statement_current_ref])
    assert not frc.write_required(data=[statement_10dayold_ref])
    assert not frc.write_required(data=[statement_new_ref])
    assert frc.write_required(data=[statement_no_retrieved])
    assert frc.write_required(data=[statement_diff_stated_in])


class fake_query_data_append_props(wdi_fastrun.FastRunContainer):
    def _query_data(self, prop_nr):
        self.prop_data['Q3402672'] = {'P527': {
            'Q3402672-11BA231B-857B-498B-AC4F-91D71EE007FD': {'qual': set(),
                                                              'ref': {
                                                                  '149c9c7ba4e246d9f09ce3ed0cdf7aa721aad5c8': {
                                                                      ('P248', 'Q3047275'),
                                                                  }},
                                                              'v': 'Q24784025'},
            'Q3402672-15F54AFF-7DCC-4DF6-A32F-73C48619B0B2': {'qual': set(),
                                                              'ref': {
                                                                  '149c9c7ba4e246d9f09ce3ed0cdf7aa721aad5c8': {
                                                                      ('P248', 'Q3047275'),
                                                                  }},
                                                              'v': 'Q24743729'},
            'Q3402672-C8F11D55-1B11-44E5-9EAF-637E062825A4': {'qual': set(),
                                                              'ref': {
                                                                  '149c9c7ba4e246d9f09ce3ed0cdf7aa721aad5c8': {
                                                                      ('P248', 'Q3047275')}},
                                                              'v': 'Q24782625'}}}

        self.rev_lookup = {'Q24784025': {'Q3402672'}}


def test_append_props():
    qid = 'Q3402672'
    # https://www.wikidata.org/wiki/Q3402672#P527

    # don't consider refs
    statements = [wdi_core.WDItemID(value='Q24784025', prop_nr='P527')]
    frc = fake_query_data_append_props(base_filter={'P352': '', 'P703': 'Q15978631'},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    assert frc.write_required(data=statements, append_props=['P527'], cqid=qid) is False
    assert frc.write_required(data=statements, cqid=qid) is True

    # if we are in append mode, and the refs are different, we should write
    statements = [wdi_core.WDItemID(value='Q24784025', prop_nr='P527')]
    frc = fake_query_data_append_props(base_filter={'P352': '', 'P703': 'Q15978631'},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                       use_refs=True)
    assert frc.write_required(data=statements, append_props=['P527'], cqid=qid) is True
    assert frc.write_required(data=statements, cqid=qid) is True


def test_ref_equals():
    # dates are a month apart
    oldref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    newref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2002-1-31T12:01:13Z', prop_nr='P813')]
    assert WDBaseDataType.refs_equal([oldref], [newref]) is False
    assert WDBaseDataType.custom_ref_equal_dates([oldref], [newref]) is True
    assert WDBaseDataType.custom_ref_equal_dates([oldref], [newref], days=10) is False


def test_ref_equals2():
    # dates are a year apart
    oldref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    newref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2003-1-31T12:01:13Z', prop_nr='P813')]
    assert WDBaseDataType.refs_equal([oldref], [newref]) is False
    assert WDBaseDataType.custom_ref_equal_dates([oldref], [newref]) is False


def test_ref_equals3():
    # dates are equal but another statement is different
    oldref = [wdi_core.WDExternalID(value='P99999', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    newref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    assert WDBaseDataType.refs_equal([oldref], [newref]) is False
    assert WDBaseDataType.custom_ref_equal_dates([oldref], [newref]) is False


def test_ref_equals4():
    # multiple refs
    oldrefs = [
        [wdi_core.WDExternalID(value='99999', prop_nr='P352')],
        [wdi_core.WDExternalID(value='11111', prop_nr='P352')]
    ]
    newrefs = [
        [wdi_core.WDExternalID(value='99999', prop_nr='P352')],
        [wdi_core.WDExternalID(value='11111', prop_nr='P352')]
    ]
    assert WDBaseDataType.refs_equal(oldrefs, newrefs) is True

    newrefs = [
        [wdi_core.WDExternalID(value='99999', prop_nr='P352')],
        [wdi_core.WDExternalID(value='123123', prop_nr='P352')]
    ]
    assert WDBaseDataType.refs_equal(oldrefs, newrefs) is False

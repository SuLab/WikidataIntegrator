from datetime import datetime

from wikidataintegrator import wdi_core, wdi_fastrun
from wikidataintegrator.wdi_core import WDBaseDataType


def test_query_data():
    """
    This hits wikidata and may change
    :return:
    """
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


def fake_query_data_doid(_):
    # all this does is set the frc.prop_data to contain one statement about blindness
    print("using fake query data")
    frc.prop_data['Q10874'] = {'P699': {
        'Q10874-7475555C-9EAB-45BB-B36B-C18AF5852FC8': {
            'qual': set(),
            'ref': {
                '04921d9e0eab8d4bbbf568fb4b06c4362d2ab57a': {
                    ('P248', 'Q28556593'),
                    ('P699', 'DOID:1432'),
                    ('P813', '+2017-01-31T00:00:00Z')}},
            'v': 'DOID:1432'}}}

    frc.rev_lookup = {'DOID:1432': {'Q10874'}}

def fake_query_data_ensembl(_):
    print("using fake query data")
    frc.prop_data['Q14911732'] = {'P594': {
        'fake statement id': {
            'qual': set(),
            'ref': {
                'fake ref id': {
                    ('P248', 'Q29458763'),
                    ('P594', 'ENSG00000123374')}},
            'v': 'ENSG00000123374'}}}

    frc.rev_lookup = {'DOID:1432': {'Q10874'}}


def test_fastrun_ref_doid():
    """
    Uses fake_query_data. Will not change
    :return:
    """
    frc = wdi_fastrun.FastRunContainer(base_filter={'P699': ''},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    frc._query_data = fake_query_data_doid

    statements = [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699')]
    assert frc.write_required(data=statements)

    statements = [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', references=[
        [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', is_reference=True),
        wdi_core.WDItemID(value='Q28556593', prop_nr='P248', is_reference=True),
        wdi_core.WDTime('+2017-02-10T00:00:00Z', prop_nr='P813', is_reference=True)]
    ])]
    assert not frc.write_required(data=statements)

    statements = [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', references=[
        [wdi_core.WDExternalID(value='DOID:1432', prop_nr='P699', is_reference=True),
         wdi_core.WDItemID(value='Q28556593', prop_nr='P248', is_reference=True),
         wdi_core.WDTime('+2018-02-10T00:00:00Z', prop_nr='P813', is_reference=True)]
    ])]
    assert frc.write_required(data=statements)

def test_fastrun_ref_ensembl():
    """
    Uses fake_query_data. Will not change
    :return:
    """
    frc = wdi_fastrun.FastRunContainer(base_filter={'P594': '', 'P703': 'Q15978631'},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    frc._query_data = fake_query_data_ensembl

    statements = [wdi_core.WDExternalID(value='ENSG00000123374', prop_nr='P594')]
    assert frc.write_required(data=statements)



def test_human_protein():
    from wikidataintegrator import wdi_core, wdi_fastrun
    qid = 'Q3402672'
    statements = [
        wdi_core.WDExternalID(value='P58743', prop_nr='P352'),
        wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
        wdi_core.WDItemID(value='Q8054', prop_nr='P31'),
        wdi_core.WDItemID(value='Q8054', prop_nr='P279'),
        wdi_core.WDItemID(value='Q14876823', prop_nr='P702'),
    ]
    frc = wdi_fastrun.FastRunContainer(base_filter={'P352': '', 'P703': 'Q15978631'},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    assert frc.write_required(data=statements, append_props=['P527']) is False
    assert frc.write_required(data=statements) is True

    from wikidataintegrator import wdi_core, wdi_fastrun
    qid = 'Q3402672'
    frc = wdi_fastrun.FastRunContainer(base_filter={'P352': '', 'P703': 'Q15978631'},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    statements = [wdi_core.WDExternalID(value='P58743', prop_nr='P352')]
    assert frc.write_required(data=statements) is False


def test_ref_equals():
    # dates are a month apart
    oldref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    newref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2002-1-31T12:01:13Z', prop_nr='P813')]
    assert WDBaseDataType.refs_equal([oldref], [newref]) is True


def test_ref_equals2():
    # dates are a year apart
    oldref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    newref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2003-1-31T12:01:13Z', prop_nr='P813')]
    assert WDBaseDataType.refs_equal([oldref], [newref]) is False


def test_ref_equals3():
    # dates are equal but another statement is diff
    oldref = [wdi_core.WDExternalID(value='P99999', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    newref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    assert WDBaseDataType.refs_equal([oldref], [newref]) is False


def test_ref_equals4():
    # multiple refs
    oldref = [wdi_core.WDExternalID(value='P99999', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    newref = [wdi_core.WDExternalID(value='P58742', prop_nr='P352'),
              wdi_core.WDItemID(value='Q24784025', prop_nr='P527'),
              wdi_core.WDTime('+2001-12-31T12:01:13Z', prop_nr='P813')]
    assert WDBaseDataType.refs_equal([oldref, oldref], [newref, newref]) is False


# mesh
from wikidataintegrator import wdi_core, wdi_fastrun

qid = 'Q5070802'

statements = [
    wdi_core.WDExternalID(value='D004630', prop_nr='P486'),
]

frc = wdi_fastrun.FastRunContainer(base_filter={'P486': ''},
                                   base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)

fast_run_result = frc.write_required(data=statements)

# 2 aulifiers
from wikidataintegrator import wdi_core, wdi_fastrun

qid = 'Q14911732'

statements = [
    wdi_core.WDExternalID(value='Q847102', prop_nr='P1057'),
]

frc = wdi_fastrun.FastRunContainer(base_filter={'P1057': '', 'P703': 'Q15978631'},
                                   base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)

fast_run_result = frc.write_required(data=statements)

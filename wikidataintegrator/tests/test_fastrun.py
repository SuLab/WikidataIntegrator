from datetime import datetime

from wikidataintegrator import wdi_core, wdi_fastrun
from wikidataintegrator.wdi_core import WDBaseDataType


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

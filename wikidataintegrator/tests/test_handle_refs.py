import copy
from wikidataintegrator import wdi_fastrun, wdi_core
from wikidataintegrator.ref_handlers import strict_overwrite
# not testing the functionality of KEEP_GOOD here, just skipping the query of all pmids
wdi_core.WDItemEngine.databases = ['a']
wdi_core.WDItemEngine.pmids = ['a']
wdi_fastrun.FastRunContainer.debug = True

"""
Tests the global ref modes: KEEP_GOOD, STRICT_OVERWRITE, STRICT_KEEP and the append mode
Tests custom ref handler strict_overwrite (as an example)
"""

# the frc class, wditemengine class and orig_statements represent the same data
class frc_fake_query_data_paper(wdi_fastrun.FastRunContainer):
    def __init__(self, *args, **kwargs):
        super(frc_fake_query_data_paper, self).__init__(*args, **kwargs)
        self.prop_dt_map = {'P527': 'wikibase-item', 'P248': 'wikibase-item', 'P698': 'external-id', 'P813': 'time'}
        self.prop_data['Q15397819'] = {'P698': {
            'fake statement id': {
                'qual': set(),
                'ref': {
                    'ref1': {
                        ('P248', 'Q5412157'),  # stated in Europe PubMed Central
                        ('P813', '+2017-01-01T00:00:00Z'),
                        ('P698', '99999999999')},
                    'ref2': {
                        ('P248', 'Q20814663'),  # stated in my little pony the movie
                        ('P3165', '1234'),  # some other ID
                    }},
                'v': '99999999999'}}}
        self.rev_lookup = {'99999999999': {'Q15397819'}}


class fake_itemengine(wdi_core.WDItemEngine):
    def get_wd_entity(self):
        # https://www.wikidata.org/w/api.php?action=wbgetclaims&entity=Q15397819&property=P698&format=json
        claims = {'claims': {
            'P698': [{'id': 'Q15397819$9460c2a2-4d42-adec-e841-9d5bbdc6695a',
                      'mainsnak': {'datatype': 'external-id',
                                   'datavalue': {'type': 'string', 'value': '99999999999'},
                                   'property': 'P698',
                                   'snaktype': 'value'},
                      'rank': 'normal',
                      'references': [{'hash': '9537cf2da990a2455ab924d027a0a1e5890bde8a',
                                      'snaks': {'P248': [{'datatype': 'wikibase-item',
                                                          'datavalue': {'type': 'wikibase-entityid',
                                                                        'value': {'entity-type': 'item',
                                                                                  'id': 'Q5412157',
                                                                                  'numeric-id': 5412157}},
                                                          'property': 'P248',
                                                          'snaktype': 'value'}],
                                                'P698': [{'datatype': 'external-id',
                                                          'datavalue': {'type': 'string', 'value': '99999999999'},
                                                          'property': 'P698',
                                                          'snaktype': 'value'}],
                                                'P813': [{'datatype': 'time',
                                                          'datavalue': {'type': 'time',
                                                                        'value': {'after': 0,
                                                                                  'before': 0,
                                                                                  'calendarmodel': 'http://www.wikidata.org/entity/Q1985727',
                                                                                  'precision': 11,
                                                                                  'time': '+2017-01-01T00:00:00Z',
                                                                                  'timezone': 0}},
                                                          'property': 'P813',
                                                          'snaktype': 'value'}]},
                                      'snaks-order': ['P248', 'P813', 'P698']},
                                     {'hash': '9d071aa99ef72e421e444cb999d582992adc4d50',
                                      'snaks': {'P248': [{'datatype': 'wikibase-item',
                                                          'datavalue': {'type': 'wikibase-entityid',
                                                                        'value': {'entity-type': 'item',
                                                                                  'id': 'Q20814663',
                                                                                  'numeric-id': 20814663}},
                                                          'property': 'P248',
                                                          'snaktype': 'value'}],
                                                'P3165': [{'datatype': 'external-id',
                                                           'datavalue': {'type': 'string', 'value': '1234'},
                                                           'property': 'P3165',
                                                           'snaktype': 'value'}]},
                                      'snaks-order': ['P248', 'P3165']}],
                      'type': 'statement'}]}}

        d = {"aliases": {},
             'descriptions': {'en': {'language': 'en', 'value': 'sdfs'}},
             'id': 'Q15397819',
             'labels': {'en': {'language': 'en',
                               'value': 'drgdsgf'}},
             'lastrevid': 478075481,
             'modified': '2017-04-24T20:24:05Z',
             'ns': 0,
             'pageid': 31211964,
             'sitelinks': {},
             'title': 'Q15397819',
             'type': 'item'
             }
        d.update(claims)
        return self.parse_wd_json(d)


orig_statements = [wdi_core.WDExternalID(value="99999999999", prop_nr="P698", references=[
    [
        wdi_core.WDItemID(value="Q5412157", prop_nr="P248", is_reference=True),
        wdi_core.WDExternalID(value="99999999999", prop_nr="P698", is_reference=True),
        wdi_core.WDTime("+2017-01-01T00:00:00Z", prop_nr="P813", is_reference=True),
    ],
    [
        wdi_core.WDItemID(value="Q20814663", prop_nr="P248", is_reference=True),
        wdi_core.WDExternalID(value="1234", prop_nr="P3165", is_reference=True),
    ]
])]


def test_no_change():
    # same as existing, no custom ref handling
    statements = copy.deepcopy(orig_statements)
    item = fake_itemengine(wd_item_id='Q20814663')
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert not require_write

    frc = frc_fake_query_data_paper(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True)
    assert not frc.write_required(data=statements)


def test_change_value():
    # change value, no custom ref handling
    statements = copy.deepcopy(orig_statements)
    statements[0].set_value("1234")
    item = fake_itemengine(wd_item_id='Q20814663')
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert require_write
    assert len(new) == 2
    assert hasattr(item.statements[0], 'remove')

    frc = frc_fake_query_data_paper(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True)
    assert frc.write_required(data=statements)


def test_append_mode():
    # change value, no custom ref handling
    statements = copy.deepcopy(orig_statements)
    statements[0].set_value("1234")
    item = fake_itemengine(wd_item_id='Q20814663', append_value=['P698'])
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert require_write
    assert len(new) == 2
    assert not hasattr(item.statements[0], 'remove')

    frc = frc_fake_query_data_paper(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True)
    assert frc.write_required(data=statements)


def test_ref_overwrite():
    # same value as existing, different ref, STRICT_OVERWRITE
    # new item should have the new ref only
    statements = copy.deepcopy(orig_statements)
    statements[0].references[0][2] = wdi_core.WDTime("+2018-04-24T00:00:00Z", prop_nr="P813", is_reference=True)
    item = fake_itemengine(wd_item_id='Q20814663', global_ref_mode="STRICT_OVERWRITE")
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    assert len(new) == 1
    assert len(new[0]['references']) == 2
    assert not hasattr(item.statements[0], 'remove')
    assert item.statements[0].references[0][2].value[0] == '+2018-04-24T00:00:00Z'

    frc = frc_fake_query_data_paper(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True)
    assert frc.write_required(data=statements)


def test_ref_keep():
    # same value as existing, different ref, STRICT_KEEP
    # new item should keep only the old ref
    statements = copy.deepcopy(orig_statements)
    statements[0].references[0][2] = wdi_core.WDTime("+2018-04-24T00:00:00Z", prop_nr="P813", is_reference=True)
    item = fake_itemengine(wd_item_id='Q20814663', global_ref_mode="STRICT_KEEP")
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    assert len(new) == 1
    assert len(new[0]['references']) == 2
    assert not hasattr(item.statements[0], 'remove')
    assert item.statements[0].references[0][1].value[0] == '+2017-01-01T00:00:00Z'

    # fast run mode doesn't follow global_ref_mode, unless it is custom
    # frc = frc_fake_query_data_paper(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True)
    # assert not frc.write_required(data=statements)


def test_custom_no_change():
    statements = copy.deepcopy(orig_statements)
    item = fake_itemengine(wd_item_id='Q20814663',ref_handler=strict_overwrite, global_ref_mode='CUSTOM')
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert not require_write

    frc = frc_fake_query_data_paper(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True,
                                    ref_handler=strict_overwrite)
    assert not frc.write_required(data=statements)

def test_custom_change_value():
    statements = copy.deepcopy(orig_statements)
    statements[0].set_value("1234")
    item = fake_itemengine(wd_item_id='Q20814663', ref_handler=strict_overwrite, global_ref_mode="CUSTOM")
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert require_write
    assert len(new) == 2
    assert hasattr(item.statements[0], 'remove')

    frc = frc_fake_query_data_paper(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True,
                                    ref_handler=strict_overwrite)
    assert frc.write_required(data=statements)

def test_custom_change_ref():
    # same value as existing, different ref
    # new item should have the new ref only
    statements = copy.deepcopy(orig_statements)
    statements[0].references[0][2] = wdi_core.WDTime("+2018-04-24T00:00:00Z", prop_nr="P813", is_reference=True)
    item = fake_itemengine(wd_item_id='Q20814663', global_ref_mode="CUSTOM", ref_handler=strict_overwrite)
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    assert len(new) == 1
    assert len(new[0]['references']) == 2
    assert not hasattr(item.statements[0], 'remove')
    assert item.statements[0].references[0][2].value[0] == '+2018-04-24T00:00:00Z'

    frc = frc_fake_query_data_paper(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True,
                                    ref_handler=strict_overwrite)
    assert frc.write_required(data=statements)
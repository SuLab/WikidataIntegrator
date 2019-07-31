
#### same as before, but with one ref
import copy

from wikidataintegrator import wdi_fastrun, wdi_core
from wikidataintegrator.ref_handlers import update_retrieved_if_new as custom_ref_handler
import pprint

class frc_fake_query_data_paper1(wdi_fastrun.FastRunContainer):
    def __init__(self, *args, **kwargs):
        super(frc_fake_query_data_paper1, self).__init__(*args, **kwargs)
        self.prop_data['Q15397819'] = {'P698': {
            'fake statement id': {
                'qual': set(),
                'ref': {
                    'ref1': {
                        ('P248', 'Q5412157'),  # stated in Europe PubMed Central
                        ('P813', '+2017-01-01T00:00:00Z'),
                        ('P698', '99999999999')},
                },
                'v': '99999999999'}}}
        self.rev_lookup = {'99999999999': {'Q15397819'}}
        self.prop_dt_map = {'P527': 'wikibase-item', 'P248': 'wikibase-item', 'P698': 'external-id', 'P813': 'time'}


class fake_itemengine1(wdi_core.WDItemEngine):
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
                                                                        'value': {
                                                                            'entity-type': 'item',
                                                                            'id': 'Q5412157',
                                                                            'numeric-id': 5412157}},
                                                          'property': 'P248',
                                                          'snaktype': 'value'}],
                                                'P698': [{'datatype': 'external-id',
                                                          'datavalue': {'type': 'string',
                                                                        'value': '99999999999'},
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
                                      'snaks-order': ['P248', 'P813', 'P698']}],
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
        print("komt ie hier")
        d.update(claims)

        pprint.pprint(d)
        return self.parse_wd_json(d)


orig_statements1 = [wdi_core.WDExternalID(value="99999999999", prop_nr="P698", references=[
    [
        wdi_core.WDItemID(value="Q5412157", prop_nr="P248", is_reference=True),
        wdi_core.WDExternalID(value="99999999999", prop_nr="P698", is_reference=True),
        wdi_core.WDTime("+2017-01-01T00:00:00Z", prop_nr="P813", is_reference=True),
    ]
])]


def test_ref_custom():
    # custom ref mode, same retrieved date
    statements = copy.deepcopy(orig_statements1)
    item = fake_itemengine1(wd_item_id='Q20814663', global_ref_mode="CUSTOM", ref_handler=custom_ref_handler)
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert not require_write

    frc = frc_fake_query_data_paper1(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True,
                                    ref_handler=custom_ref_handler)
    frc.debug = True
    assert not frc.write_required(data=statements)

def test_ref_custom_append():
    # custom ref mode, diff value, append prop
    statements = copy.deepcopy(orig_statements1)
    statements[0].set_value("new value")
    item = fake_itemengine1(wd_item_id='Q20814663', global_ref_mode="CUSTOM", ref_handler=custom_ref_handler, append_value=['P698'])
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert require_write

    frc = frc_fake_query_data_paper1(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True,
                                    ref_handler=custom_ref_handler)
    frc.debug = True
    assert frc.write_required(data=statements, append_props=['P698'])

    ## nothing new
    statements = copy.deepcopy(orig_statements1)
    item = fake_itemengine1(wd_item_id='Q20814663', global_ref_mode="CUSTOM", ref_handler=custom_ref_handler,
                            append_value=['P698'])
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert not require_write

    frc = frc_fake_query_data_paper1(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                     use_refs=True,
                                     ref_handler=custom_ref_handler)
    frc.debug = True
    assert not frc.write_required(data=statements, append_props=['P698'])


def test_ref_custom_diff_date_year():
    # replace retrieved date, one year away. should be updated
    statements = copy.deepcopy(orig_statements1)
    statements[0].references[0][2] = wdi_core.WDTime("+2018-04-24T00:00:00Z", prop_nr="P813", is_reference=True)
    item = fake_itemengine1(wd_item_id='Q20814663', global_ref_mode="CUSTOM", ref_handler=custom_ref_handler)
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert require_write

    frc = frc_fake_query_data_paper1(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True,
                                    ref_handler=custom_ref_handler)
    frc.debug = True
    assert frc.write_required(data=statements)


def test_ref_custom_diff_date_month():
    # replace retrieved date, one month away, should not be updated
    statements = copy.deepcopy(orig_statements1)
    statements[0].references[0][2] = wdi_core.WDTime("+2017-02-01T00:00:00Z", prop_nr="P813", is_reference=True)
    item = fake_itemengine1(wd_item_id='Q20814663', global_ref_mode="CUSTOM", ref_handler=custom_ref_handler)
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert not require_write

    frc = frc_fake_query_data_paper1(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True,
                                    ref_handler=custom_ref_handler)
    frc.debug = True
    assert not frc.write_required(data=statements)


def test_ref_custom_diff_stated_in():
    # diff ref stated in
    statements = copy.deepcopy(orig_statements1)
    statements[0].references[0][0] = wdi_core.WDItemID("Q123", prop_nr="P813", is_reference=True)
    item = fake_itemengine1(wd_item_id='Q20814663', global_ref_mode="CUSTOM", ref_handler=custom_ref_handler)
    orig = item.wd_json_representation['claims']['P698']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P698']
    require_write = not all(
        any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert require_write

    frc = frc_fake_query_data_paper1(base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine, use_refs=True,
                                    ref_handler=custom_ref_handler)
    frc.debug = True
    assert frc.write_required(data=statements)

test_ref_custom()
from wikidataintegrator import wdi_core
from wikidataintegrator.wdi_core import WDBaseDataType


class dmc2l_itemengine(wdi_core.WDItemEngine):
    def get_wd_entity(self):
        # https://www.wikidata.org/w/index.php?title=Q29566137&oldid=478075481
        d = {'aliases': {},
             'claims': {'P2249': [{'id': 'Q29566137$66AC8DA1-A5C4-46B2-BB6B-2C46170FE617',
                                   'mainsnak': {'datatype': 'external-id',
                                                'datavalue': {'type': 'string', 'value': 'NT_033779'},
                                                'property': 'P2249',
                                                'snaktype': 'value'},
                                   'rank': 'normal',
                                   'references': [{'hash': 'ed2b62a2428e55901a8164dea2bbc0ff88ce4656',
                                                   'snaks': {'P2249': [{'datatype': 'external-id',
                                                                        'datavalue': {'type': 'string',
                                                                                      'value': 'NT_033779'},
                                                                        'property': 'P2249',
                                                                        'snaktype': 'value'}],
                                                             'P248': [{'datatype': 'wikibase-item',
                                                                       'datavalue': {'type': 'wikibase-entityid',
                                                                                     'value': {'entity-type': 'item',
                                                                                               'id': 'Q20641742',
                                                                                               'numeric-id': 20641742}},
                                                                       'property': 'P248',
                                                                       'snaktype': 'value'}],
                                                             'P813': [{'datatype': 'time',
                                                                       'datavalue': {'type': 'time',
                                                                                     'value': {'after': 0,
                                                                                               'before': 0,
                                                                                               'calendarmodel': 'http://www.wikidata.org/entity/Q1985727',
                                                                                               'precision': 11,
                                                                                               'time': '+2017-04-24T00:00:00Z',
                                                                                               'timezone': 0}},
                                                                       'property': 'P813',
                                                                       'snaktype': 'value'}]},
                                                   'snaks-order': ['P248', 'P2249', 'P813']}],
                                   'type': 'statement'}],
                        'P31': [{'id': 'Q29566137$5218B3AA-9862-484D-B274-624AFAD9EA87',
                                 'mainsnak': {'datatype': 'wikibase-item',
                                              'datavalue': {'type': 'wikibase-entityid',
                                                            'value': {'entity-type': 'item', 'id': 'Q37748',
                                                                      'numeric-id': 37748}},
                                              'property': 'P31',
                                              'snaktype': 'value'},
                                 'rank': 'normal',
                                 'references': [{'hash': 'ed2b62a2428e55901a8164dea2bbc0ff88ce4656',
                                                 'snaks': {'P2249': [{'datatype': 'external-id',
                                                                      'datavalue': {'type': 'string',
                                                                                    'value': 'NT_033779'},
                                                                      'property': 'P2249',
                                                                      'snaktype': 'value'}],
                                                           'P248': [{'datatype': 'wikibase-item',
                                                                     'datavalue': {'type': 'wikibase-entityid',
                                                                                   'value': {'entity-type': 'item',
                                                                                             'id': 'Q20641742',
                                                                                             'numeric-id': 20641742}},
                                                                     'property': 'P248',
                                                                     'snaktype': 'value'}],
                                                           'P813': [{'datatype': 'time',
                                                                     'datavalue': {'type': 'time',
                                                                                   'value': {'after': 0,
                                                                                             'before': 0,
                                                                                             'calendarmodel': 'http://www.wikidata.org/entity/Q1985727',
                                                                                             'precision': 11,
                                                                                             'time': '+2017-04-24T00:00:00Z',
                                                                                             'timezone': 0}},
                                                                     'property': 'P813',
                                                                     'snaktype': 'value'}]},
                                                 'snaks-order': ['P248', 'P2249', 'P813']}],
                                 'type': 'statement'}],
                        'P703': [{'id': 'Q29566137$8F1FCC77-B35E-44C7-A67B-DF2BA4ED3838',
                                  'mainsnak': {'datatype': 'wikibase-item',
                                               'datavalue': {'type': 'wikibase-entityid',
                                                             'value': {'entity-type': 'item', 'id': 'Q130888',
                                                                       'numeric-id': 130888}},
                                               'property': 'P703',
                                               'snaktype': 'value'},
                                  'rank': 'normal',
                                  'references': [{'hash': 'ed2b62a2428e55901a8164dea2bbc0ff88ce4656',
                                                  'snaks': {'P2249': [{'datatype': 'external-id',
                                                                       'datavalue': {'type': 'string',
                                                                                     'value': 'NT_033779'},
                                                                       'property': 'P2249',
                                                                       'snaktype': 'value'}],
                                                            'P248': [{'datatype': 'wikibase-item',
                                                                      'datavalue': {'type': 'wikibase-entityid',
                                                                                    'value': {'entity-type': 'item',
                                                                                              'id': 'Q20641742',
                                                                                              'numeric-id': 20641742}},
                                                                      'property': 'P248',
                                                                      'snaktype': 'value'}],
                                                            'P813': [{'datatype': 'time',
                                                                      'datavalue': {'type': 'time',
                                                                                    'value': {'after': 0,
                                                                                              'before': 0,
                                                                                              'calendarmodel': 'http://www.wikidata.org/entity/Q1985727',
                                                                                              'precision': 11,
                                                                                              'time': '+2017-04-24T00:00:00Z',
                                                                                              'timezone': 0}},
                                                                      'property': 'P813',
                                                                      'snaktype': 'value'}]},
                                                  'snaks-order': ['P248', 'P2249', 'P813']}],
                                  'type': 'statement'}]},
             'descriptions': {'en': {'language': 'en', 'value': 'chromosome'}},
             'id': 'Q29566137',
             'labels': {'en': {'language': 'en',
                               'value': 'Drosophila melanogaster chromosome 2L'}},
             'lastrevid': 478075481,
             'modified': '2017-04-24T20:24:05Z',
             'ns': 0,
             'pageid': 31211964,
             'sitelinks': {},
             'title': 'Q29566137',
             'type': 'item'}

        return self.parse_wd_json(d)


def test_no_change():
    # same as existing
    statements = [wdi_core.WDExternalID(value="NT_033779", prop_nr="P2249", references=[[
        wdi_core.WDItemID(value="Q20641742", prop_nr="P248", is_reference=True),
        wdi_core.WDExternalID(value="NT_033779", prop_nr="P2249", is_reference=True),
        wdi_core.WDTime("+2017-04-24T00:00:00Z", prop_nr="P813", is_reference=True),
    ]])]
    item = dmc2l_itemengine(wd_item_id='Q29566137', global_ref_mode='CUSTOM', ref_comparison_f=WDBaseDataType.custom_ref_equal_dates)
    orig = item.wd_json_representation['claims']['P2249']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P2249']
    require_write = not all(any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert not require_write

def test_change_value():
    # change value
    statements = [wdi_core.WDExternalID(value="face", prop_nr="P2249", references=[[
        wdi_core.WDItemID(value="Q20641742", prop_nr="P248", is_reference=True),
        wdi_core.WDExternalID(value="NT_033779", prop_nr="P2249", is_reference=True),
        wdi_core.WDTime("+2017-04-24T00:00:00Z", prop_nr="P813", is_reference=True),
    ]])]
    item = dmc2l_itemengine(wd_item_id='Q29566137', global_ref_mode='CUSTOM', ref_comparison_f=WDBaseDataType.custom_ref_equal_dates)
    orig = item.wd_json_representation['claims']['P2249']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P2249']
    require_write = not all(any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert require_write

def test_month_ref():
    # ref is one month old
    statements = [wdi_core.WDExternalID(value="NT_033779", prop_nr="P2249", references=[[
        wdi_core.WDItemID(value="Q20641742", prop_nr="P248", is_reference=True),
        wdi_core.WDExternalID(value="NT_033779", prop_nr="P2249", is_reference=True),
        wdi_core.WDTime("+2017-05-24T00:00:00Z", prop_nr="P813", is_reference=True),
    ]])]
    item = dmc2l_itemengine(wd_item_id='Q29566137', global_ref_mode='CUSTOM', ref_comparison_f=WDBaseDataType.custom_ref_equal_dates)
    orig = item.wd_json_representation['claims']['P2249']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P2249']
    require_write = not all(any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert not require_write

def test_year_ref():
    # ref is one year old
    statements = [wdi_core.WDExternalID(value="NT_033779", prop_nr="P2249", references=[[
        wdi_core.WDItemID(value="Q20641742", prop_nr="P248", is_reference=True),
        wdi_core.WDExternalID(value="NT_033779", prop_nr="P2249", is_reference=True),
        wdi_core.WDTime("+2018-05-24T00:00:00Z", prop_nr="P813", is_reference=True),
    ]])]
    item = dmc2l_itemengine(wd_item_id='Q29566137', global_ref_mode='CUSTOM', ref_comparison_f=WDBaseDataType.custom_ref_equal_dates)
    orig = item.wd_json_representation['claims']['P2249']
    item.update(data=statements)
    new = item.wd_json_representation['claims']['P2249']
    require_write = not all(any(x.equals(y, include_ref=True) for y in item.original_statements) for x in item.statements)
    assert require_write

from wikidataintegrator import wdi_core, wdi_fastrun
wdi_fastrun.FastRunContainer.debug = True


def test_query_data():
    """
    test_fastrun.test_query_data
    This hits live wikidata and may change !!

    This tests that the fast run container correctly queries data from wikidata and stores it in the appropriate format
    without getting references
    """
    frc = wdi_fastrun.FastRunContainer(base_filter={'P699': ''},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    # get a string value
    frc._query_data('P699')
    # wikidata-item value
    frc._query_data('P31')
    # uri value
    frc._query_data('P1709')

    # https://www.wikidata.org/wiki/Q10874
    assert 'Q10874' in frc.prop_data
    assert 'P699' in frc.prop_data['Q10874']
    # the ID may change, so retrieve it
    statement_id = list(frc.prop_data['Q10874']['P699'].keys())[0]
    d = frc.prop_data['Q10874']['P699'][statement_id]
    # d looks like: {'qual': set(), 'ref': {}, 'v': 'DOID:1432'}
    assert all(x in d for x in {'qual', 'ref', 'v'})
    assert frc.prop_data['Q10874']['P699'][statement_id]['v'].startswith('DOID:')

    # uri
    # temporarily stop of test below
    # v = set([x['v'] for x in frc.prop_data['Q18211153']['P1709'].values()])
    # assert all(y.startswith("http") for y in v)


def test_query_data_ref():
    """
    test_fastrun.test_query_data_ref
    This hits live wikidata and may change !!

    This tests that the fast run container correctly queries data from wikidata and stores it in the appropriate format
    WITH getting references
    """
    frc = wdi_fastrun.FastRunContainer(base_filter={'P699': ''}, base_data_type=wdi_core.WDBaseDataType,
                                       engine=wdi_core.WDItemEngine, use_refs=True)
    frc._query_data('P699')

    # https://www.wikidata.org/wiki/Q10874
    assert 'Q10874' in frc.prop_data
    assert 'P699' in frc.prop_data['Q10874']
    # the ID may change, so retrieve it
    statement_id = list(frc.prop_data['Q10874']['P699'].keys())[0]
    d = frc.prop_data['Q10874']['P699'][statement_id]
    # d looks like:
    """
    {'qual': set(),
     'ref': {'16c138dfc51df49853f1a9d79f31e2234853842c': {('P248', 'Q30988716'),
            ('P699', 'DOID:1432'),
            ('P813', '+2017-07-05T00:00:00Z')}},
      'v': 'DOID:1432'}
    """
    assert all(x in d for x in {'qual', 'ref', 'v'})
    assert frc.prop_data['Q10874']['P699'][statement_id]['v'].startswith('DOID:')
    assert len(d['ref']) > 0
    ref_id = list(d['ref'].keys())[0]
    ref = d['ref'][ref_id]
    assert len(ref) > 1


class frc_fake_query_data_ensembl(wdi_fastrun.FastRunContainer):
    def __init__(self, *args, **kwargs):
        super(frc_fake_query_data_ensembl, self).__init__(*args, **kwargs)
        self.prop_dt_map = {'P248': 'wikibase-item', 'P594': 'external-id'}
        self.prop_data['Q14911732'] = {'P594': {
            'fake statement id': {
                'qual': set(),
                'ref': {'fake ref id': {
                    ('P248', 'Q29458763'),  # stated in ensembl Release 88
                    ('P594', 'ENSG00000123374')}},
                'v': 'ENSG00000123374'}}}
        self.rev_lookup = {'ENSG00000123374': {'Q14911732'}}


class frc_fake_query_data_ensembl_no_ref(wdi_fastrun.FastRunContainer):
    def __init__(self, *args, **kwargs):
        super(frc_fake_query_data_ensembl_no_ref, self).__init__(*args, **kwargs)
        self.prop_dt_map = {'P248': 'wikibase-item', 'P594': 'external-id'}
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
    frc.debug = True
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


class fake_query_data_append_props(wdi_fastrun.FastRunContainer):
    # an item with three values for the same property
    def __init__(self, *args, **kwargs):
        super(fake_query_data_append_props, self).__init__(*args, **kwargs)
        self.prop_dt_map = {'P527': 'wikibase-item', 'P248': 'wikibase-item', 'P594': 'external-id'}
        self.rev_lookup = {
            'Q24784025': {'Q3402672'},
            'Q24743729': {'Q3402672'},
            'Q24782625': {'Q3402672'},
        }
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


def test_append_props():
    qid = 'Q3402672'
    # https://www.wikidata.org/wiki/Q3402672#P527

    # don't consider refs
    statements = [wdi_core.WDItemID(value='Q24784025', prop_nr='P527')]
    frc = fake_query_data_append_props(base_filter={'P352': '', 'P703': 'Q15978631'},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine)
    assert frc.write_required(data=statements, append_props=['P527'], cqid=qid) is False
    assert frc.write_required(data=statements, cqid=qid)

    # if we are in append mode, and the refs are different, we should write
    statements = [wdi_core.WDItemID(value='Q24784025', prop_nr='P527')]
    frc = fake_query_data_append_props(base_filter={'P352': '', 'P703': 'Q15978631'},
                                       base_data_type=wdi_core.WDBaseDataType, engine=wdi_core.WDItemEngine,
                                       use_refs=True)
    assert frc.write_required(data=statements, append_props=['P527'], cqid=qid) is True
    assert frc.write_required(data=statements, cqid=qid)
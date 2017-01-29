from wikidataintegrator.wdi_helpers import PubmedItem, Release, id_mapper


def test_get_pubmed_item():
    # this one exists
    wdid = PubmedItem(1234).get_or_create()
    assert wdid == "Q27442302"


def test_get_pubmed_item_cache():
    # this one exists
    wdid = PubmedItem(1234).get_or_create()
    assert '1234' in PubmedItem._cache
    assert PubmedItem._cache['1234'] == "Q27442302"


def test_pubmedstub_bad_pmid():
    # invalid pubmed id
    wdid = PubmedItem(999999999).get_or_create(login='fake login')
    assert wdid is None


def test_release_lookup_database():
    r = Release("Ensembl Release 85", "Release 85 of Ensembl", "85", edition_of="Ensembl")
    assert r.edition_of_wdid == 'Q1344256'


def test_release_lookup_release():
    r = Release("Ensembl Release 85", "Release 85 of Ensembl", "85", edition_of="Ensembl")
    assert r.get_or_create() == 'Q27666311'
    assert 'Q1344256' in Release._release_cache
    assert '85' in Release._release_cache['Q1344256']


def test_release_new_item_no_write():
    r = Release("Ensembl Release 85", "Release 85 of Ensembl", "XXX", edition_of_wdid='Q1344256')
    try:
        r.get_or_create()
    except ValueError as e:
        assert "login required to create item" == str(e)


def test_id_mapper():
    # get all uniprot to wdid, where taxon is human
    d = id_mapper("P352",(("P703", "Q15978631"),))
    assert 100000 > len(d) > 20000

    d = id_mapper("P683", raise_on_duplicate=False, return_as_set=True)
    assert '3978' in d
    assert type(d['3978']) == set

    # should raise error
    raised = False
    try:
        d = id_mapper("P492", raise_on_duplicate=True)
    except ValueError:
        raised = True
    assert raised
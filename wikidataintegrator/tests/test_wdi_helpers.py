from wikidataintegrator.wdi_helpers import PubmedItem, Release


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

"""
custom ref handler:
overwrite a reference if the `stated in` is in `old_stated_in`
otherwise keep it and append a new ref

"""


def update_release(olditem, newitem, old_stated_in=None, stated_in_pid='P248', retrieved_pid='P813'):
    if not old_stated_in:
        old_stated_in = set()

    def is_equal_not_retrieved_stated_in(oldref, newref):
        # Return True if the oldref == newref, NOT including any "retrieved" or stated in statements
        if len(oldref) != len(newref):
            return False
        oldref_minus = [x for x in oldref if x.get_prop_nr() not in {retrieved_pid, stated_in_pid}]
        newref_minus = [x for x in newref if x.get_prop_nr() not in {retrieved_pid, stated_in_pid}]
        if not all(x in oldref_minus for x in newref_minus):
            return False
        return True

    def ref_overwrite(oldref, newref):
        if get_stated_in_value(oldref) & old_stated_in:
            # the old ref has a stated in that is `old`, so should be removed
            return True
        else:
            return False

    def get_stated_in_value(ref):
        stated_in_value = set(["Q{}".format(x.get_value()) for x in ref if x.get_prop_nr() == stated_in_pid])
        return stated_in_value

    newrefs = newitem.references
    oldrefs = olditem.references

    found_mate = [False] * len(newrefs)
    for new_n, newref in enumerate(newrefs):
        for old_n, oldref in enumerate(oldrefs):
            if is_equal_not_retrieved_stated_in(oldref, newref):
                found_mate[new_n] = True
                if ref_overwrite(oldref, newref):
                    oldrefs[old_n] = newref
    for f_idx, f in enumerate(found_mate):
        if not f:
            oldrefs.append(newrefs[f_idx])

"""
# todo: this needs to be integrated into a test system on a separate test wikibase
# todo: need another test for adding a ref with a release on an existing statement with no old release
from wikidataintegrator import wdi_core, wdi_login, wdi_helpers, ref_handlers
from functools import partial

mediawiki_api_url = "http://localhost:7171/w/api.php"
sparql_endpoint_url = "http://localhost:7272/proxy/wdqs/bigdata/namespace/wdq/sparql"
h = wdi_helpers.WikibaseHelper(sparql_endpoint_url)
stated_in = h.get_pid("P248")
retrieved = h.get_pid("P813")
doid = h.get_pid("P699")
login = wdi_login.WDLogin("testbot", "password", mediawiki_api_url=mediawiki_api_url)

# set the statement on sandbox, along with 2 other refs
s = wdi_core.WDExternalID("C1234", "P31", references=[
    [wdi_core.WDItemID("Q53798", stated_in, is_reference=True),
     wdi_core.WDTime("+2018-01-01T00:00:00Z", retrieved, is_reference=True),
     wdi_core.WDExternalID("DOID:0060852", doid, is_reference=True)],
    [wdi_core.WDItemID("Q123", stated_in, is_reference=True)],
    [wdi_core.WDExternalID("123", doid, is_reference=True)],
])

item = wdi_core.WDItemEngine(wd_item_id="Q80983", data=[s],
                             mediawiki_api_url=mediawiki_api_url, sparql_endpoint_url=sparql_endpoint_url)
item.write(login)

# update the stated in
s = wdi_core.WDExternalID("C1234", "P31", references=[
    [wdi_core.WDItemID("Q45050", stated_in, is_reference=True),
     wdi_core.WDTime("+2019-02-01T00:00:00Z", retrieved, is_reference=True),
     wdi_core.WDExternalID("DOID:0060852", doid, is_reference=True)]])


ref_handler = partial(ref_handlers.update_release, old_stated_in={'Q53798'},
                      stated_in_pid=stated_in, retrieved_pid=retrieved)
item = wdi_core.WDItemEngine(wd_item_id="Q80983", data=[s],
                             mediawiki_api_url=mediawiki_api_url, sparql_endpoint_url=sparql_endpoint_url,
                             ref_handler=ref_handler, global_ref_mode="CUSTOM")
item.write(login)
"""
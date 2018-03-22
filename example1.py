from wikidataintegrator import wdi_core

my_first_wikidata_item = wdi_core.WDItemEngine(wd_item_id='Q5')

# to check successful installation and retrieval of the data, you can print the json representation of the item
print my_first_wikidata_item.get_wd_json_representation()

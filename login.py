__author__ = 'sebastian'

"""
login routine for Wikidata
"""

def login():
    # Login to wikidata
    site = pywikibot.Site("wikidata", "wikidata")
    repo = site.data_repository()
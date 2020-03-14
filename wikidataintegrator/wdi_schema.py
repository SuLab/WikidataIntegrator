"""
Authors:
  Andra Waagmeester (andra' at ' micelio.be)

This file is part of the WikidataIntegrator.

"""

__author__ = 'Andra Waagmeester'
__license__ = 'MIT'

class WikibaseSchemaEngine(object):
    def __init__(self,shex_url="https://www.wikidata.org/wiki/Special:EntitySchemaText/E37"):
        self.shex_url = shex_url



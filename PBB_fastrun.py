import PBB_Core
import os
import json
import pprint

prefix = '''
    PREFIX wd: <http://www.wikidata.org/entity/>
    PREFIX wdt: <http://www.wikidata.org/prop/direct/>
    PREFIX p: <http://www.wikidata.org/prop/>
    PREFIX ps: <http://www.wikidata.org/prop/statement/>
    PREFIX pq: <http://www.wikidata.org/prop/qualifier/>
    '''


class FastRunContainer(object):

    def __init__(self):
        self.data = []
        self.prop_list = []
        self.active_hrs = []
        self.statements = []

    def check_data(self, data):
        pass

    def get_data(self):
        return self.data

    def _query_data(self, prop_nr):
        pass

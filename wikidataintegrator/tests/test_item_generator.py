import unittest
import pprint
import sys
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login

__author__ = 'Sebastian Burgstaller-Muehlbacher'
__license__ = 'AGPLv3'


class TestItemGenerator(unittest.TestCase):

    def test_item_generator(self):
        items = ['Q408883', 'Q5', 'P715']

        # login_obj = wdi_login.WDLogin(user='', '')
        login_obj = None
        item_instances = wdi_core.WDItemEngine.generate_item_instances(items=items, server='www.wikidata.org',
                                                                       login=login_obj)

        for qid, item in item_instances:
            print(qid)
            pprint.pprint(item.entity_metadata)

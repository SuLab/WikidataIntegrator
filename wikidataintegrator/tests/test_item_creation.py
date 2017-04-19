import unittest
import pprint
import sys
from wikidataintegrator import wdi_core, wdi_fastrun, wdi_login

__author__ = 'Sebastian Burgstaller-Muehlbacher'
__license__ = 'AGPLv3'


class TestItemCreation(unittest.TestCase):

    def test_new_item_creation(self):
        data = [
            wdi_core.WDString(value='test', prop_nr='P716'),
            wdi_core.WDString(value='test1', prop_nr='P76')
        ]

        item = wdi_core.WDItemEngine(item_name='dae', domain=None, data=data)

        pprint.pprint(item.get_wd_json_representation())

        if not item.get_wd_json_representation():
            raise ValueError



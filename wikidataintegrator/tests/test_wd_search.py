import unittest
from wikidataintegrator import wdi_core

__author__ = 'Sebastian Burgstaller-Muehlbacher'
__license__ = 'AGPLv3'


class TestWDSearch(unittest.TestCase):

    def test_wd_search(self):
        t = wdi_core.WDItemEngine.get_wd_search_results('rivaroxaban')

        print(t)
        print('Number of results: ', len(t))
        self.assertIsNot(len(t), 0)

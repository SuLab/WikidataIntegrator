import unittest
import sys

from .. import wdi_core

class TestItemCreation(unittest.TestCase):
    def test_new_item_creation(self):
        data = [
            wdi_core.WDString(value='test', prop_nr='P1'),
            wdi_core.WDString(value='test1', prop_nr='P2'),
            wdi_core.WDMath("xxx", prop_nr="P3"),
            wdi_core.WDExternalID("xxx", prop_nr="P4"),
            wdi_core.WDItemID("Q123", prop_nr="P5"),
            wdi_core.WDTime('+%Y-%m-%dT%H:%M:%SZ', "P6"),
            wdi_core.WDUrl("http://www.google.com", "P7"),
            wdi_core.WDMonolingualText("xxx", prop_nr="P8"),
            wdi_core.WDQuantity(5, prop_nr="P9"),
            wdi_core.WDQuantity(5, upper_bound=9, lower_bound=2, prop_nr="P10"),
            wdi_core.WDCommonsMedia("xxx", prop_nr="P11"),
            wdi_core.WDGlobeCoordinate(1.2345, 1.2345, 12, prop_nr="P12"),
            wdi_core.WDGeoShape("Data:xxx.map", prop_nr="P13"),
            wdi_core.WDProperty("P123", "P14"),
            wdi_core.WDTabularData("Data:xxx.tab", prop_nr="P15"),
            wdi_core.WDMusicalNotation("\relative c' { c d e f | g2 g | a4 a a a | g1 |}", prop_nr="P16"),
            wdi_core.WDLexeme("L123", prop_nr="P17"),
            wdi_core.WDForm("L123-F123", prop_nr="P18"),
            wdi_core.WDSense("L123-S123", prop_nr="P19")
        ]
        core_props = set(["P{}".format(x) for x in range(20)])

        for d in data:
            item = wdi_core.WDItemEngine(new_item=True, data=[d], core_props=core_props)
            assert item.get_wd_json_representation()
            item = wdi_core.WDItemEngine(new_item=True, data=[d], core_props=set())
            assert item.get_wd_json_representation()

        item = wdi_core.WDItemEngine(new_item=True, data=data, core_props=core_props)
        assert item.get_wd_json_representation()
        item = wdi_core.WDItemEngine(new_item=True, data=data, core_props=set())
        assert item.get_wd_json_representation()

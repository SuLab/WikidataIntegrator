import json
import os
import unittest

from pyshex.utils.schema_loader import SchemaLoader
from unittest import mock
from wikidataintegrator import wbs_core

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

def mocked_request_properties_once(_):
    res = mock.Mock()
    res.text = json.dumps({
        "batchcomplete":"",
        "query":{
            "pages":{
                "2":{"pageid":2, "title":"Property:P1", "terms":{"label":["genomic start"]}},
                "11":{"pageid":11, "title":"Property:P10", "terms":{"label":["instance of"]}}
            }
        }
    })
    return res

def mocked_request_properties_empty(_):
    res = mock.Mock()
    res.text = json.dumps({"batchcomplete": ""})
    return res

def mocked_request_properties_gapcontinue(_):
    res = mock.Mock()
    res.text = json.dumps({
        "batchcomplete":"",
        "continue": {"gapcontinue": 'P1', "continue": "gapcontinue||"},
        "query":{
            "pages":{
                "4":{"pageid":4, "title":"Property:P4", "terms":{"label":["Ensembl transcript ID"]}},
                "15":{"pageid":15, "title":"Property:P9", "terms":{"label":["chromosome"]}}
            }
        }
    })
    return res

class TestWBSCore(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_test_shex('test_schema.shex')
        self.mocked_wbengine = wbs_core.WikibaseEngine('www.example.org')
        self.mocked_wbengine.getNamespace = unittest.mock.Mock()
        self.mocked_wbengine.getNamespace.side_effect = "P5"

    def test_init(self):
        endpoint = 'http://example.org'
        wb_engine = wbs_core.WikibaseEngine(endpoint)
        self.assertEqual(wb_engine.wikibase_url, endpoint)
        self.assertEqual(wb_engine.wikibase_api, f"{endpoint}/w/api.php")

    @mock.patch('requests.get', side_effect=mocked_request_properties_empty)
    def test_list_properties_empty(self, mock_get):
        result = self.mocked_wbengine.listProperties()
        self.assertListEqual(result, [])

    @mock.patch('requests.get', side_effect=mocked_request_properties_once)
    def test_list_properties_once(self, mock_get):
        result = self.mocked_wbengine.listProperties()
        expected = ["genomic start", "instance of"]
        self.assertListEqual(result, expected)

    @mock.patch('requests.get', side_effect=[mocked_request_properties_gapcontinue(None),
                                             mocked_request_properties_once(None)])
    def test_list_properties_gapcontinue(self, mock_get):
        result = self.mocked_wbengine.listProperties()
        expected = ["Ensembl transcript ID", "chromosome", "genomic start", "instance of"]
        self.assertListEqual(result, expected)

    def test_get_namespace(self):
        pass

    def test_extract_properties(self):
        properties = []
        wbs_core.WikibaseEngine.extractProperties(self.model, properties)
        expected = []
        self.assertListEqual(properties, expected)

    def _load_test_shex(self, file_name):
        with open(os.path.join(TEST_DATA_DIR, file_name), 'r', encoding='utf-8') as f:
            shex = f.read()
            loader = SchemaLoader()
            schema = loader.loads(shex)
            self.model = json.loads(schema._as_json_dumps())

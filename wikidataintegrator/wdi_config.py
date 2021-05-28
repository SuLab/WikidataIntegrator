"""
Config global options
Options can be changed at run time. See tests/test_backoff.py for usage example

Options:
BACKOFF_MAX_TRIES: maximum number of times to retry failed request to wikidata endpoint.
        Default: None (retry indefinitely)
        To disable retry, set value to 1
BACKOFF_MAX_VALUE: maximum number of seconds to wait before retrying. wait time will increase to this number
        Default: 3600 (one hour)
USER_AGENT_DEFAULT: default user agent string used for http requests. Both to wikibase api, query service and others.
    See: https://meta.wikimedia.org/wiki/User-Agent_policy
"""
import pkg_resources

try:
    __version__ = pkg_resources.get_distribution("wikidataintegrator").version
except Exception as e:
    __version__ = ""

config = {
    'BACKOFF_MAX_TRIES': None,
    'BACKOFF_MAX_VALUE': 3600,
    'USER_AGENT_DEFAULT': 'wikidataintegrator/{}'.format(__version__),
    'MAXLAG': 5,
    'PROPERTY_CONSTRAINT_PID': 'P2302',
    'DISTINCT_VALUES_CONSTRAINT_QID': 'Q21502410',
    'COORDINATE_GLOBE_QID': 'http://www.wikidata.org/entity/Q2',
    'CALENDAR_MODEL_QID': 'http://www.wikidata.org/entity/Q1985727',
    'MEDIAWIKI_API_URL': 'https://www.wikidata.org/w/api.php',
    'MEDIAWIKI_INDEX_URL': 'https://www.wikidata.org/w/index.php',
    'SPARQL_ENDPOINT_URL': 'https://query.wikidata.org/sparql',
    "ENTITY_SCHEMA_REPO": "https://www.wikidata.org/wiki/Special:EntitySchemaText/",
    'WIKIBASE_URL': 'http://www.wikidata.org',
    'CONCEPT_BASE_URI': 'http://www.wikidata.org/entity/'
}

prefix = {
	'ontolex' : 'http://www.w3.org/ns/lemon/ontolex#',
    'dct' : 'http://purl.org/dc/terms/',
	'rdfs' : 'http://www.w3.org/2000/01/rdf-schema#',
	'owl' : 'http://www.w3.org/2002/07/owl#',
	'wikibase' : 'http://wikiba.se/ontology#',
	'skos' : 'http://www.w3.org/2004/02/skos/core#',
	'schema' : 'http://schema.org/',
	'cc' : 'http://creativecommons.org/ns#',
	'geo' : 'http://www.opengis.net/ont/geosparql#',
	'prov' : 'http://www.w3.org/ns/prov#',
	'wd' : 'http://www.wikidata.org/entity/',
	'data' : 'https://www.wikidata.org/wiki/Special:EntityData/',
	's' : 'http://www.wikidata.org/entity/statement/',
	'ref' : 'http://www.wikidata.org/reference/',
	'v' : 'http://www.wikidata.org/value/',
	'wdt' : 'http://www.wikidata.org/prop/direct/',
	'wdtn' : 'http://www.wikidata.org/prop/direct-normalized/',
	'p' : 'http://www.wikidata.org/prop/',
	'ps' : 'http://www.wikidata.org/prop/statement/',
	'psv' : 'http://www.wikidata.org/prop/statement/value/',
	'psn' : 'http://www.wikidata.org/prop/statement/value-normalized/',
	'pq' : 'http://www.wikidata.org/prop/qualifier/',
	'pqv' : 'http://www.wikidata.org/prop/qualifier/value/',
	'pqn' : 'http://www.wikidata.org/prop/qualifier/value-normalized/',
	'pr' : 'http://www.wikidata.org/prop/reference/',
	'prv' : 'http://www.wikidata.org/prop/reference/value/',
	'prn' : 'http://www.wikidata.org/prop/reference/value-normalized/',
	'wdno' : 'http://www.wikidata.org/prop/novalue/',
}

property_value_types = {'commonsMedia': 'http://wikiba.se/ontology#CommonsMedia' ,
                'external-id': 'http://wikiba.se/ontology#ExternalId' ,
                'geo-shape': 'http://wikiba.se/ontology#GeoShape',
                'globe-coordinate': 'http://wikiba.se/ontology#GlobeCoordinate',
                'math': 'http://wikiba.se/ontology#Math',
                'monolingualtext': 'http://wikiba.se/ontology#Monolingualtext',
                'quantity': 'http://wikiba.se/ontology#Quantity',
                'string': 'http://wikiba.se/ontology#String',
                'tabular-data': 'http://wikiba.se/ontology#TabularData',
                'time': 'http://wikiba.se/ontology#Time',
                'edtf': '<http://wikiba.se/ontology#Edtf>',
                'url': 'http://wikiba.se/ontology#Url',
                'wikibase-item': 'http://wikiba.se/ontology#WikibaseItem',
                'wikibase-property': 'http://wikiba.se/ontology#WikibaseProperty',
                'lexeme': 'http://wikiba.se/ontology#WikibaseLexeme',
                'form': 'http://wikiba.se/ontology#WikibaseForm',
                'sense': 'http://wikiba.se/ontology#WikibaseSense',
                'musical-notation': 'http://wikiba.se/ontology#MusicalNotation',
                'schema': 'http://schema.org/'
                }
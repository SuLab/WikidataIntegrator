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

unit_conversion_rules = {
    "Q199": {
        "factor": "1",
        "unit": "Q199",
        "label": "1",
        "siLabel": "1"
    },
    "Q531": {
        "factor": "9460800000000000",
        "unit": "Q11573",
        "label": "light-year",
        "siLabel": "metre"
    },
    "Q573": {
        "factor": "86400",
        "unit": "Q11574",
        "label": "day",
        "siLabel": "second"
    },
    "Q577": {
        "factor": "31536000",
        "unit": "Q11574",
        "label": "year",
        "siLabel": "second"
    },
    "Q1811": {
        "factor": "149597870700",
        "unit": "Q11573",
        "label": "astronomical unit",
        "siLabel": "metre"
    },
    "Q2101": {
        "factor": "0.0000000000000000001602176634",
        "unit": "Q25406",
        "label": "elementary charge",
        "siLabel": "coulomb"
    },
    "Q3710": {
        "factor": "0.3048006",
        "unit": "Q11573",
        "label": "foot",
        "siLabel": "metre"
    },
    "Q7727": {
        "factor": "60",
        "unit": "Q11574",
        "label": "minute",
        "siLabel": "second"
    },
    "Q11229": {
        "factor": "0.01",
        "unit": "Q199",
        "label": "percent",
        "siLabel": "1"
    },
    "Q11570": {
        "factor": "1",
        "unit": "Q11570",
        "label": "kilogram",
        "siLabel": "kilogram"
    },
    "Q11573": {
        "factor": "1",
        "unit": "Q11573",
        "label": "metre",
        "siLabel": "metre"
    },
    "Q11574": {
        "factor": "1",
        "unit": "Q11574",
        "label": "second",
        "siLabel": "second"
    },
    "Q11579": {
        "factor": "1",
        "unit": "Q11579",
        "label": "kelvin",
        "siLabel": "kelvin"
    },
    "Q11582": {
        "factor": "0.001",
        "unit": "Q25517",
        "label": "litre",
        "siLabel": "cubic metre"
    },
    "Q12129": {
        "factor": "30856775814913700",
        "unit": "Q11573",
        "label": "parsec",
        "siLabel": "metre"
    },
    "Q12438": {
        "factor": "1",
        "unit": "Q12438",
        "label": "newton",
        "siLabel": "newton"
    },
    "Q19828": {
        "factor": "31622400",
        "unit": "Q11574",
        "label": "leap year",
        "siLabel": "second"
    },
    "Q21131": {
        "factor": "0.000000000333564095198152049575576714474918511792581519845972909698748992544702375401318468125038689265491795660850147",
        "unit": "Q25406",
        "label": "statcoulomb",
        "siLabel": "coulomb"
    },
    "Q23387": {
        "factor": "604800",
        "unit": "Q11574",
        "label": "week",
        "siLabel": "second"
    },
    "Q25235": {
        "factor": "3600",
        "unit": "Q11574",
        "label": "hour",
        "siLabel": "second"
    },
    "Q25236": {
        "factor": "1",
        "unit": "Q25236",
        "label": "watt",
        "siLabel": "watt"
    },
    "Q25250": {
        "factor": "1",
        "unit": "Q25250",
        "label": "volt",
        "siLabel": "volt"
    },
    "Q25269": {
        "factor": "1",
        "unit": "Q25269",
        "label": "joule",
        "siLabel": "joule"
    },
    "Q25272": {
        "factor": "1",
        "unit": "Q25272",
        "label": "ampere",
        "siLabel": "ampere"
    },
    "Q25343": {
        "factor": "1",
        "unit": "Q25343",
        "label": "square metre",
        "siLabel": "square metre"
    },
    "Q25406": {
        "factor": "1",
        "unit": "Q25406",
        "label": "coulomb",
        "siLabel": "coulomb"
    },
    "Q25517": {
        "factor": "1",
        "unit": "Q25517",
        "label": "cubic metre",
        "siLabel": "cubic metre"
    },
    "Q28390": {
        "factor": "0.01745329251994329576923690768488612713",
        "unit": "Q33680",
        "label": "degree",
        "siLabel": "radian"
    },
    "Q33680": {
        "factor": "1",
        "unit": "Q33680",
        "label": "radian",
        "siLabel": "radian"
    },
    "Q35852": {
        "factor": "10000",
        "unit": "Q25343",
        "label": "hectare",
        "siLabel": "square metre"
    },
    "Q36384": {
        "factor": "1",
        "unit": "Q41509",
        "label": "molar equivalent",
        "siLabel": "mole"
    },
    "Q39274": {
        "factor": "1000000",
        "unit": "Q794261",
        "label": "sverdrup",
        "siLabel": "cubic metre per second"
    },
    "Q39369": {
        "factor": "1",
        "unit": "Q39369",
        "label": "hertz",
        "siLabel": "hertz"
    },
    "Q40603": {
        "factor": "0.0000000000000000000000000000033356409519815204957557671447491851179258151984597290969874899254470237540131846812503868926549",
        "unit": "Q28739766",
        "label": "debye",
        "siLabel": "coulomb metre"
    },
    "Q41509": {
        "factor": "1",
        "unit": "Q41509",
        "label": "mole",
        "siLabel": "mole"
    },
    "Q41803": {
        "factor": "0.001",
        "unit": "Q11570",
        "label": "gram",
        "siLabel": "kilogram"
    },
    "Q42764": {
        "factor": "10000",
        "unit": "Q11573",
        "label": "Scandinavian mile",
        "siLabel": "metre"
    },
    "Q44395": {
        "factor": "1",
        "unit": "Q44395",
        "label": "pascal",
        "siLabel": "pascal"
    },
    "Q47083": {
        "factor": "1",
        "unit": "Q47083",
        "label": "ohm",
        "siLabel": "ohm"
    },
    "Q48013": {
        "factor": "0.028349523125",
        "unit": "Q11570",
        "label": "ounce",
        "siLabel": "kilogram"
    },
    "Q48440": {
        "factor": "695700000",
        "unit": "Q11573",
        "label": "solar radius",
        "siLabel": "metre"
    },
    "Q81292": {
        "factor": "4046.8564224",
        "unit": "Q25343",
        "label": "acre",
        "siLabel": "square metre"
    },
    "Q81454": {
        "factor": "0.0000000001",
        "unit": "Q11573",
        "label": "\u00e5ngstr\u00f6m",
        "siLabel": "metre"
    },
    "Q83216": {
        "factor": "1",
        "unit": "Q83216",
        "label": "candela",
        "siLabel": "candela"
    },
    "Q83327": {
        "factor": "0.000000000000000000160217656535",
        "unit": "Q25269",
        "label": "electronvolt",
        "siLabel": "joule"
    },
    "Q93318": {
        "factor": "1852",
        "unit": "Q11573",
        "label": "nautical mile",
        "siLabel": "metre"
    },
    "Q100995": {
        "factor": "0.45359237",
        "unit": "Q11570",
        "label": "pound",
        "siLabel": "kilogram"
    },
    "Q102573": {
        "factor": "1",
        "unit": "Q102573",
        "label": "becquerel",
        "siLabel": "becquerel"
    },
    "Q103246": {
        "factor": "1",
        "unit": "Q103246",
        "label": "sievert",
        "siLabel": "sievert"
    },
    "Q103510": {
        "factor": "100000",
        "unit": "Q44395",
        "label": "bar",
        "siLabel": "pascal"
    },
    "Q128822": {
        "factor": "0.5144444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444444",
        "unit": "Q182429",
        "label": "knot",
        "siLabel": "metre per second"
    },
    "Q130964": {
        "factor": "4.184",
        "unit": "Q25269",
        "label": "small calorie",
        "siLabel": "joule"
    },
    "Q131255": {
        "factor": "1",
        "unit": "Q131255",
        "label": "farad",
        "siLabel": "farad"
    },
    "Q160857": {
        "factor": "735.49875",
        "unit": "Q25236",
        "label": "metric Horsepower",
        "siLabel": "watt"
    },
    "Q163343": {
        "factor": "1",
        "unit": "Q163343",
        "label": "tesla",
        "siLabel": "tesla"
    },
    "Q163354": {
        "factor": "1",
        "unit": "Q163354",
        "label": "henry",
        "siLabel": "henry"
    },
    "Q169893": {
        "factor": "1",
        "unit": "Q169893",
        "label": "siemens",
        "siLabel": "siemens"
    },
    "Q170804": {
        "factor": "1",
        "unit": "Q170804",
        "label": "weber",
        "siLabel": "weber"
    },
    "Q174728": {
        "factor": "0.01",
        "unit": "Q11573",
        "label": "centimetre",
        "siLabel": "metre"
    },
    "Q174789": {
        "factor": "0.001",
        "unit": "Q11573",
        "label": "millimetre",
        "siLabel": "metre"
    },
    "Q175821": {
        "factor": "0.000001",
        "unit": "Q11573",
        "label": "micrometre",
        "siLabel": "metre"
    },
    "Q177493": {
        "factor": "0.0001",
        "unit": "Q163343",
        "label": "gauss",
        "siLabel": "tesla"
    },
    "Q177612": {
        "factor": "1",
        "unit": "Q177612",
        "label": "steradian",
        "siLabel": "steradian"
    },
    "Q177974": {
        "factor": "101325",
        "unit": "Q44395",
        "label": "standard atmosphere",
        "siLabel": "pascal"
    },
    "Q178674": {
        "factor": "0.000000001",
        "unit": "Q11573",
        "label": "nanometre",
        "siLabel": "metre"
    },
    "Q179836": {
        "factor": "1",
        "unit": "Q179836",
        "label": "lux",
        "siLabel": "lux"
    },
    "Q180154": {
        "factor": "0.2777777777777777778",
        "unit": "Q182429",
        "label": "kilometre per hour",
        "siLabel": "metre per second"
    },
    "Q180892": {
        "factor": "1988550000000000000000000000000",
        "unit": "Q11570",
        "label": "solar mass",
        "siLabel": "kilogram"
    },
    "Q181011": {
        "factor": "0.001",
        "unit": "Q199",
        "label": "per mille",
        "siLabel": "1"
    },
    "Q182098": {
        "factor": "3600000",
        "unit": "Q25269",
        "label": "kilowatt hour",
        "siLabel": "joule"
    },
    "Q182429": {
        "factor": "1",
        "unit": "Q182429",
        "label": "metre per second",
        "siLabel": "metre per second"
    },
    "Q185078": {
        "factor": "100",
        "unit": "Q25343",
        "label": "are",
        "siLabel": "square metre"
    },
    "Q185153": {
        "factor": "0.0000001",
        "unit": "Q25269",
        "label": "erg",
        "siLabel": "joule"
    },
    "Q185648": {
        "factor": "133.3223684211",
        "unit": "Q44395",
        "label": "torr",
        "siLabel": "pascal"
    },
    "Q185759": {
        "factor": "0.2286",
        "unit": "Q11573",
        "label": "span",
        "siLabel": "metre"
    },
    "Q185789": {
        "factor": "0.00000005",
        "unit": "Q25517",
        "label": "drop",
        "siLabel": "cubic metre"
    },
    "Q190095": {
        "factor": "1",
        "unit": "Q190095",
        "label": "gray",
        "siLabel": "gray"
    },
    "Q191118": {
        "factor": "1000",
        "unit": "Q11570",
        "label": "tonne",
        "siLabel": "kilogram"
    },
    "Q192274": {
        "factor": "0.000000000001",
        "unit": "Q11573",
        "label": "picometre",
        "siLabel": "metre"
    },
    "Q193933": {
        "factor": "1",
        "unit": "Q11547251",
        "label": "dioptre",
        "siLabel": "reciprocal metre"
    },
    "Q200323": {
        "factor": "0.1",
        "unit": "Q11573",
        "label": "decimetre",
        "siLabel": "metre"
    },
    "Q201933": {
        "factor": "0.00001",
        "unit": "Q12438",
        "label": "dyne",
        "siLabel": "newton"
    },
    "Q202642": {
        "factor": "0.00000000000000000000000000000000000000000005391247",
        "unit": "Q11574",
        "label": "Planck time",
        "siLabel": "second"
    },
    "Q204759": {
        "factor": "2.48",
        "unit": "Q11573",
        "label": "skewed sazhen",
        "siLabel": "metre"
    },
    "Q206037": {
        "factor": "0.0166667",
        "unit": "Q6137407",
        "label": "revolutions per minute",
        "siLabel": "reciprocal second"
    },
    "Q207387": {
        "factor": "0.00000000000000000000000000000000001616255",
        "unit": "Q11573",
        "label": "Planck length",
        "siLabel": "metre"
    },
    "Q207733": {
        "factor": "1066.781",
        "unit": "Q11573",
        "label": "verst",
        "siLabel": "metre"
    },
    "Q208528": {
        "factor": "0.015707963267949",
        "unit": "Q33680",
        "label": "gradian",
        "siLabel": "radian"
    },
    "Q208634": {
        "factor": "1",
        "unit": "Q208634",
        "label": "katal",
        "siLabel": "katal"
    },
    "Q208788": {
        "factor": "0.000000000000001",
        "unit": "Q11573",
        "label": "femtometre",
        "siLabel": "metre"
    },
    "Q209351": {
        "factor": "0.0000000000000000000000000001",
        "unit": "Q25343",
        "label": "barn",
        "siLabel": "square metre"
    },
    "Q209426": {
        "factor": "0.0002908882086657215961539484614147687855738119814236209093495319066951681857672415739470402616057515803687174154178965098747",
        "unit": "Q33680",
        "label": "minute of arc",
        "siLabel": "radian"
    },
    "Q211256": {
        "factor": "0.44704",
        "unit": "Q182429",
        "label": "mile per hour",
        "siLabel": "metre per second"
    },
    "Q211580": {
        "factor": "1054.35026444",
        "unit": "Q25269",
        "label": "British thermal unit (thermochemical)",
        "siLabel": "joule"
    },
    "Q212120": {
        "factor": "3600",
        "unit": "Q25406",
        "label": "ampere hour",
        "siLabel": "coulomb"
    },
    "Q215571": {
        "factor": "1",
        "unit": "Q215571",
        "label": "newton metre",
        "siLabel": "newton metre"
    },
    "Q216795": {
        "factor": "1000",
        "unit": "Q25343",
        "label": "dunam",
        "siLabel": "square metre"
    },
    "Q216880": {
        "factor": "9.80665",
        "unit": "Q12438",
        "label": "kilogram-force",
        "siLabel": "newton"
    },
    "Q217208": {
        "factor": "31557600",
        "unit": "Q11574",
        "label": "Julian year",
        "siLabel": "second"
    },
    "Q218593": {
        "factor": "0.0254",
        "unit": "Q11573",
        "label": "inch",
        "siLabel": "metre"
    },
    "Q229354": {
        "factor": "37000000000",
        "unit": "Q102573",
        "label": "curie",
        "siLabel": "becquerel"
    },
    "Q232291": {
        "factor": "2589988.110336",
        "unit": "Q25343",
        "label": "square mile",
        "siLabel": "square metre"
    },
    "Q235729": {
        "factor": "31536000",
        "unit": "Q11574",
        "label": "common year",
        "siLabel": "second"
    },
    "Q239830": {
        "factor": "6.525",
        "unit": "Q3395194",
        "label": "Planck momentum",
        "siLabel": "newton second"
    },
    "Q249439": {
        "factor": "0.00000000000000000187554603778",
        "unit": "Q25406",
        "label": "Planck charge",
        "siLabel": "coulomb"
    },
    "Q251545": {
        "factor": "2518",
        "unit": "Q25343",
        "label": "jugerum",
        "siLabel": "square metre"
    },
    "Q253276": {
        "factor": "1609.344",
        "unit": "Q11573",
        "label": "mile",
        "siLabel": "metre"
    },
    "Q254532": {
        "factor": "0.0003046174197867085993467435493788935535590647965197774884695478202537050871117038655247460927073627232044452442522846649407",
        "unit": "Q177612",
        "label": "square degree",
        "siLabel": "steradian"
    },
    "Q256422": {
        "factor": "149597870000000000",
        "unit": "Q11573",
        "label": "siriometre",
        "siLabel": "metre"
    },
    "Q260126": {
        "factor": "0.01",
        "unit": "Q103246",
        "label": "Roentgen equivalent man",
        "siLabel": "sievert"
    },
    "Q261247": {
        "factor": "0.0002",
        "unit": "Q11570",
        "label": "carat",
        "siLabel": "kilogram"
    },
    "Q267391": {
        "factor": "100",
        "unit": "Q11547251",
        "label": "kayser",
        "siLabel": "reciprocal metre"
    },
    "Q267637": {
        "factor": "1000000",
        "unit": "Q102573",
        "label": "rutherford",
        "siLabel": "becquerel"
    },
    "Q281096": {
        "factor": "1",
        "unit": "Q281096",
        "label": "candela per square metre",
        "siLabel": "candela per square metre"
    },
    "Q296936": {
        "factor": "41868000000",
        "unit": "Q25269",
        "label": "tonne of oil equivalent",
        "siLabel": "joule"
    },
    "Q304479": {
        "factor": "6.283185307179586",
        "unit": "Q33680",
        "label": "turn",
        "siLabel": "radian"
    },
    "Q319686": {
        "factor": "299792458",
        "unit": "Q182429",
        "label": "speed of gravity",
        "siLabel": "metre per second"
    },
    "Q321017": {
        "factor": "0.000258",
        "unit": "Q28683485",
        "label": "roentgen",
        "siLabel": "coulomb per kilogram"
    },
    "Q335320": {
        "factor": "0.022225",
        "unit": "Q11573",
        "label": "finger",
        "siLabel": "metre"
    },
    "Q341454": {
        "factor": "0.0000445",
        "unit": "Q11570",
        "label": "Acino",
        "siLabel": "kilogram"
    },
    "Q342590": {
        "factor": "1233.4818",
        "unit": "Q25517",
        "label": "acre-foot",
        "siLabel": "cubic metre"
    },
    "Q352599": {
        "factor": "0.001823",
        "unit": "Q11570",
        "label": "adarme",
        "siLabel": "kilogram"
    },
    "Q388886": {
        "factor": "0.00000000000000000000000697",
        "unit": "Q11574",
        "label": "chronon",
        "siLabel": "second"
    },
    "Q414263": {
        "factor": "0.51711",
        "unit": "Q25517",
        "label": "culleus",
        "siLabel": "cubic metre"
    },
    "Q469356": {
        "factor": "907.18474",
        "unit": "Q11570",
        "label": "short ton",
        "siLabel": "kilogram"
    },
    "Q473913": {
        "factor": "0.2034",
        "unit": "Q25517",
        "label": "Q473913",
        "siLabel": "cubic metre"
    },
    "Q475145": {
        "factor": "0.00417",
        "unit": "Q11570",
        "label": "Zuz",
        "siLabel": "kilogram"
    },
    "Q476572": {
        "factor": "0.00000000000000000435974434",
        "unit": "Q25269",
        "label": "hartree",
        "siLabel": "joule"
    },
    "Q482798": {
        "factor": "0.9144",
        "unit": "Q11573",
        "label": "yard",
        "siLabel": "metre"
    },
    "Q483261": {
        "factor": "0.0000000000000000000000000016605388",
        "unit": "Q11570",
        "label": "dalton",
        "siLabel": "kilogram"
    },
    "Q484092": {
        "factor": "1",
        "unit": "Q484092",
        "label": "lumen",
        "siLabel": "lumen"
    },
    "Q494083": {
        "factor": "201.168",
        "unit": "Q11573",
        "label": "furlong",
        "siLabel": "metre"
    },
    "Q495983": {
        "factor": "2756.25",
        "unit": "Q25343",
        "label": "aroura",
        "siLabel": "square metre"
    },
    "Q500515": {
        "factor": "0.01",
        "unit": "Q1051665",
        "label": "gal",
        "siLabel": "metre per square second"
    },
    "Q514845": {
        "factor": "1000",
        "unit": "Q44395",
        "label": "pi\u00e8ze",
        "siLabel": "pascal"
    },
    "Q536785": {
        "factor": "5155000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "unit": "Q844211",
        "label": "Planck density",
        "siLabel": "kilogram per cubic metre"
    },
    "Q550341": {
        "factor": "1",
        "unit": "Q550341",
        "label": "volt ampere",
        "siLabel": "volt ampere"
    },
    "Q552299": {
        "factor": "20.11684",
        "unit": "Q11573",
        "label": "chain",
        "siLabel": "metre"
    },
    "Q591259": {
        "factor": "2419200",
        "unit": "Q11574",
        "label": "lunar month",
        "siLabel": "second"
    },
    "Q592634": {
        "factor": "0.00000002176434",
        "unit": "Q11570",
        "label": "Planck mass",
        "siLabel": "kilogram"
    },
    "Q605704": {
        "factor": "12",
        "unit": "Q199",
        "label": "dozen",
        "siLabel": "1"
    },
    "Q608697": {
        "factor": "0.00000001",
        "unit": "Q170804",
        "label": "maxwell",
        "siLabel": "weber"
    },
    "Q613726": {
        "factor": "1000000000000000000000",
        "unit": "Q11570",
        "label": "yottagram",
        "siLabel": "kilogram"
    },
    "Q619941": {
        "factor": "0.3183098861837906715377675267450287240689192914809128974953346881177935952684530701802276055325061719121456854535159160737858",
        "unit": "Q281096",
        "label": "apostilb",
        "siLabel": "candela per square metre"
    },
    "Q626299": {
        "factor": "6894.757",
        "unit": "Q44395",
        "label": "pound per square inch",
        "siLabel": "pascal"
    },
    "Q630369": {
        "factor": "1",
        "unit": "Q630369",
        "label": "volt-ampere reactive",
        "siLabel": "volt-ampere reactive"
    },
    "Q636200": {
        "factor": "0.000000016667",
        "unit": "Q208634",
        "label": "enzyme unit",
        "siLabel": "katal"
    },
    "Q640907": {
        "factor": "10000",
        "unit": "Q281096",
        "label": "stilb",
        "siLabel": "candela per square metre"
    },
    "Q651336": {
        "factor": "1898130000000000000000000000",
        "unit": "Q11570",
        "label": "Jupiter mass",
        "siLabel": "kilogram"
    },
    "Q652571": {
        "factor": "0.0000000000529177",
        "unit": "Q11573",
        "label": "Bohr radius",
        "siLabel": "metre"
    },
    "Q654875": {
        "factor": "500",
        "unit": "Q11573",
        "label": "Li",
        "siLabel": "metre"
    },
    "Q667419": {
        "factor": "1016.0469088",
        "unit": "Q11570",
        "label": "long ton",
        "siLabel": "kilogram"
    },
    "Q669909": {
        "factor": "0.008736",
        "unit": "Q25517",
        "label": "modius",
        "siLabel": "cubic metre"
    },
    "Q669931": {
        "factor": "10926.512",
        "unit": "Q25343",
        "label": "dessiatin",
        "siLabel": "square metre"
    },
    "Q681996": {
        "factor": "5972190000000000000000000",
        "unit": "Q11570",
        "label": "Earth mass",
        "siLabel": "kilogram"
    },
    "Q685662": {
        "factor": "463300000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "unit": "Q44395",
        "label": "Planck pressure",
        "siLabel": "pascal"
    },
    "Q691310": {
        "factor": "39.3701",
        "unit": "Q11547251",
        "label": "mesh",
        "siLabel": "reciprocal metre"
    },
    "Q691543": {
        "factor": "1.4787",
        "unit": "Q11573",
        "label": "pace",
        "siLabel": "metre"
    },
    "Q693944": {
        "factor": "0.00006479891",
        "unit": "Q11570",
        "label": "grain",
        "siLabel": "kilogram"
    },
    "Q706688": {
        "factor": "3.30578512397",
        "unit": "Q25343",
        "label": "pyeong",
        "siLabel": "square metre"
    },
    "Q712226": {
        "factor": "1000000",
        "unit": "Q25343",
        "label": "square kilometre",
        "siLabel": "square metre"
    },
    "Q717310": {
        "factor": "2500",
        "unit": "Q25343",
        "label": "Morgen",
        "siLabel": "square metre"
    },
    "Q717727": {
        "factor": "400",
        "unit": "Q25343",
        "label": "Ngan",
        "siLabel": "square metre"
    },
    "Q720055": {
        "factor": "141678400000000000000000000000000",
        "unit": "Q11579",
        "label": "Planck temperature",
        "siLabel": "kelvin"
    },
    "Q723733": {
        "factor": "0.001",
        "unit": "Q11574",
        "label": "millisecond",
        "siLabel": "second"
    },
    "Q730251": {
        "factor": "1.3558179483314004",
        "unit": "Q25269",
        "label": "foot-pound",
        "siLabel": "joule"
    },
    "Q732707": {
        "factor": "1000000",
        "unit": "Q39369",
        "label": "megahertz",
        "siLabel": "hertz"
    },
    "Q743895": {
        "factor": "0.016666666666666666",
        "unit": "Q39369",
        "label": "beats per minute",
        "siLabel": "hertz"
    },
    "Q748716": {
        "factor": "0.3048",
        "unit": "Q182429",
        "label": "foot per second",
        "siLabel": "metre per second"
    },
    "Q751310": {
        "factor": "1",
        "unit": "Q21016931",
        "label": "poiseuille",
        "siLabel": "pascal second"
    },
    "Q752079": {
        "factor": "2.83",
        "unit": "Q25517",
        "label": "gross register ton",
        "siLabel": "cubic metre"
    },
    "Q752197": {
        "factor": "1000",
        "unit": "Q13035094",
        "label": "kilojoule per mole",
        "siLabel": "joule per mole"
    },
    "Q767390": {
        "factor": "31104000",
        "unit": "Q11574",
        "label": "Tun",
        "siLabel": "second"
    },
    "Q769996": {
        "factor": "0.00451165812456",
        "unit": "Q11573",
        "label": "cicero",
        "siLabel": "metre"
    },
    "Q786499": {
        "factor": "0.408",
        "unit": "Q11570",
        "label": "Q786499",
        "siLabel": "kilogram"
    },
    "Q794261": {
        "factor": "1",
        "unit": "Q794261",
        "label": "cubic metre per second",
        "siLabel": "cubic metre per second"
    },
    "Q804537": {
        "factor": "12441600000",
        "unit": "Q11574",
        "label": "baktun",
        "siLabel": "second"
    },
    "Q809678": {
        "factor": "0.1",
        "unit": "Q44395",
        "label": "barye",
        "siLabel": "pascal"
    },
    "Q828224": {
        "factor": "1000",
        "unit": "Q11573",
        "label": "kilometre",
        "siLabel": "metre"
    },
    "Q829073": {
        "factor": "0.0000048481368110954",
        "unit": "Q33680",
        "label": "arcsecond",
        "siLabel": "radian"
    },
    "Q829397": {
        "factor": "0.2183",
        "unit": "Q11570",
        "label": "Bes",
        "siLabel": "kilogram"
    },
    "Q834105": {
        "factor": "1",
        "unit": "Q844211",
        "label": "gram per litre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q836651": {
        "factor": "666.66666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666667",
        "unit": "Q25343",
        "label": "mu",
        "siLabel": "square metre"
    },
    "Q838801": {
        "factor": "0.000000001",
        "unit": "Q11574",
        "label": "nanosecond",
        "siLabel": "second"
    },
    "Q842015": {
        "factor": "0.000001",
        "unit": "Q11574",
        "label": "microsecond",
        "siLabel": "second"
    },
    "Q842981": {
        "factor": "105480400",
        "unit": "Q25269",
        "label": "therm (US)",
        "siLabel": "joule"
    },
    "Q843877": {
        "factor": "382800000000000000000000000",
        "unit": "Q25236",
        "label": "solar luminosity",
        "siLabel": "watt"
    },
    "Q844211": {
        "factor": "1",
        "unit": "Q844211",
        "label": "kilogram per cubic metre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q844338": {
        "factor": "100",
        "unit": "Q11573",
        "label": "hectometre",
        "siLabel": "metre"
    },
    "Q844976": {
        "factor": "79.577471545947667884441881686257181017229822870228224373833672029448398817113267545056901383126542978036421363378979018446456",
        "unit": "Q2844478",
        "label": "oersted",
        "siLabel": "ampere per metre"
    },
    "Q848856": {
        "factor": "10",
        "unit": "Q11573",
        "label": "decametre",
        "siLabel": "metre"
    },
    "Q850029": {
        "factor": "0.4578",
        "unit": "Q11570",
        "label": "mina",
        "siLabel": "kilogram"
    },
    "Q850880": {
        "factor": "0.24553779",
        "unit": "Q11570",
        "label": "Q850880",
        "siLabel": "kilogram"
    },
    "Q854546": {
        "factor": "1000000000",
        "unit": "Q11573",
        "label": "gigametre",
        "siLabel": "metre"
    },
    "Q856240": {
        "factor": "0.000471947443",
        "unit": "Q794261",
        "label": "cubic foot per minute",
        "siLabel": "cubic metre per second"
    },
    "Q857027": {
        "factor": "0.09290304",
        "unit": "Q25343",
        "label": "square foot",
        "siLabel": "square metre"
    },
    "Q857913": {
        "factor": "0.97512",
        "unit": "Q25517",
        "label": "Bierlast",
        "siLabel": "cubic metre"
    },
    "Q864818": {
        "factor": "10",
        "unit": "Q25272",
        "label": "abampere",
        "siLabel": "ampere"
    },
    "Q865954": {
        "factor": "0.001632",
        "unit": "Q11570",
        "label": "Q865954",
        "siLabel": "kilogram"
    },
    "Q876237": {
        "factor": "0.0303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303",
        "unit": "Q11573",
        "label": "cun",
        "siLabel": "metre"
    },
    "Q876244": {
        "factor": "0.05",
        "unit": "Q11570",
        "label": "tael",
        "siLabel": "kilogram"
    },
    "Q892596": {
        "factor": "0.5",
        "unit": "Q11570",
        "label": "catty",
        "siLabel": "kilogram"
    },
    "Q899762": {
        "factor": "185.3184",
        "unit": "Q11573",
        "label": "cable length (imperial)",
        "siLabel": "metre"
    },
    "Q901492": {
        "factor": "10000",
        "unit": "Q179836",
        "label": "phot",
        "siLabel": "lux"
    },
    "Q902274": {
        "factor": "0.981",
        "unit": "Q83216",
        "label": "candlepower",
        "siLabel": "candela"
    },
    "Q904031": {
        "factor": "88765.244",
        "unit": "Q11574",
        "label": "sol",
        "siLabel": "second"
    },
    "Q905912": {
        "factor": "3183.0988618379067153776752674502872406891929148091289749533468811779359526845307018022760553250617191214568545351591607378582",
        "unit": "Q281096",
        "label": "lambert",
        "siLabel": "candela per square metre"
    },
    "Q906223": {
        "factor": "1000000000000000000",
        "unit": "Q11574",
        "label": "exasecond",
        "siLabel": "second"
    },
    "Q909066": {
        "factor": "98066.5",
        "unit": "Q44395",
        "label": "technical atmosphere",
        "siLabel": "pascal"
    },
    "Q909315": {
        "factor": "299792458",
        "unit": "Q11573",
        "label": "light-second",
        "siLabel": "metre"
    },
    "Q910311": {
        "factor": "1",
        "unit": "Q910311",
        "label": "lumen second",
        "siLabel": "lumen second"
    },
    "Q911730": {
        "factor": "0.001",
        "unit": "Q179836",
        "label": "Nox",
        "siLabel": "lux"
    },
    "Q913365": {
        "factor": "1956100000",
        "unit": "Q25269",
        "label": "Planck energy",
        "siLabel": "joule"
    },
    "Q914151": {
        "factor": "36283100000000000000000000000000000000000000000000000",
        "unit": "Q25236",
        "label": "Planck power",
        "siLabel": "watt"
    },
    "Q915169": {
        "factor": "121027000000000000000000000000000000000000000",
        "unit": "Q12438",
        "label": "Planck force",
        "siLabel": "newton"
    },
    "Q920297": {
        "factor": "3.624556363776",
        "unit": "Q25517",
        "label": "cord",
        "siLabel": "cubic metre"
    },
    "Q921083": {
        "factor": "0.0032798",
        "unit": "Q25517",
        "label": "garniec",
        "siLabel": "cubic metre"
    },
    "Q923539": {
        "factor": "16.3804964",
        "unit": "Q11570",
        "label": "pood",
        "siLabel": "kilogram"
    },
    "Q931805": {
        "factor": "0.30303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303",
        "unit": "Q11573",
        "label": "shaku",
        "siLabel": "metre"
    },
    "Q935614": {
        "factor": "1600",
        "unit": "Q25343",
        "label": "rai",
        "siLabel": "square metre"
    },
    "Q939499": {
        "factor": "0.003829",
        "unit": "Q25517",
        "label": "hin",
        "siLabel": "cubic metre"
    },
    "Q940052": {
        "factor": "100",
        "unit": "Q11570",
        "label": "centner",
        "siLabel": "kilogram"
    },
    "Q974493": {
        "factor": "0.00236",
        "unit": "Q25517",
        "label": "board foot",
        "siLabel": "cubic metre"
    },
    "Q997297": {
        "factor": "1.67",
        "unit": "Q11573",
        "label": "bu",
        "siLabel": "metre"
    },
    "Q999285": {
        "factor": "0.000378",
        "unit": "Q11570",
        "label": "candareen",
        "siLabel": "kilogram"
    },
    "Q1005712": {
        "factor": "0.0166666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666667",
        "unit": "Q39369",
        "label": "actions per minute",
        "siLabel": "hertz"
    },
    "Q1022113": {
        "factor": "0.000001",
        "unit": "Q25517",
        "label": "cubic centimetre",
        "siLabel": "cubic metre"
    },
    "Q1040401": {
        "factor": "10",
        "unit": "Q11574",
        "label": "decasecond",
        "siLabel": "second"
    },
    "Q1040427": {
        "factor": "100",
        "unit": "Q11574",
        "label": "hectosecond",
        "siLabel": "second"
    },
    "Q1048969": {
        "factor": "0.233856",
        "unit": "Q11570",
        "label": "Cologne mark",
        "siLabel": "kilogram"
    },
    "Q1050958": {
        "factor": "3386.389",
        "unit": "Q44395",
        "label": "inch of mercury",
        "siLabel": "pascal"
    },
    "Q1051665": {
        "factor": "1",
        "unit": "Q1051665",
        "label": "metre per square second",
        "siLabel": "metre per square second"
    },
    "Q1052397": {
        "factor": "0.01",
        "unit": "Q190095",
        "label": "rad",
        "siLabel": "gray"
    },
    "Q1054140": {
        "factor": "1000000",
        "unit": "Q11573",
        "label": "megametre",
        "siLabel": "metre"
    },
    "Q1057069": {
        "factor": "0.1",
        "unit": "Q11570",
        "label": "hectogram",
        "siLabel": "kilogram"
    },
    "Q1063756": {
        "factor": "1",
        "unit": "Q1063756",
        "label": "radian per second",
        "siLabel": "radian per second"
    },
    "Q1065153": {
        "factor": "0.001",
        "unit": "Q33680",
        "label": "milliradian",
        "siLabel": "radian"
    },
    "Q1066138": {
        "factor": "1000000000000000",
        "unit": "Q11574",
        "label": "petasecond",
        "siLabel": "second"
    },
    "Q1067722": {
        "factor": "0.000333",
        "unit": "Q11573",
        "label": "French gauge",
        "siLabel": "metre"
    },
    "Q1072404": {
        "factor": "0.04166666667",
        "unit": "Q199",
        "label": "carat",
        "siLabel": "1"
    },
    "Q1076762": {
        "factor": "0.00312",
        "unit": "Q25517",
        "label": "chous",
        "siLabel": "cubic metre"
    },
    "Q1091059": {
        "factor": "0.000000001",
        "unit": "Q47083",
        "label": "abohm",
        "siLabel": "ohm"
    },
    "Q1091257": {
        "factor": "0.000001",
        "unit": "Q25999243",
        "label": "tex",
        "siLabel": "kilogram per metre"
    },
    "Q1092296": {
        "factor": "31556926",
        "unit": "Q11574",
        "label": "annum",
        "siLabel": "second"
    },
    "Q1095649": {
        "factor": "0.00084",
        "unit": "Q25517",
        "label": "Icce",
        "siLabel": "cubic metre"
    },
    "Q1098949": {
        "factor": "4.184",
        "unit": "Q21393312",
        "label": "clausius",
        "siLabel": "joule per kelvin"
    },
    "Q1101932": {
        "factor": "0.052176",
        "unit": "Q25517",
        "label": "medimnos",
        "siLabel": "cubic metre"
    },
    "Q1102701": {
        "factor": "3",
        "unit": "Q11570",
        "label": "Clove",
        "siLabel": "kilogram"
    },
    "Q1131660": {
        "factor": "6.35029318",
        "unit": "Q11570",
        "label": "stone",
        "siLabel": "kilogram"
    },
    "Q1152139": {
        "factor": "10000",
        "unit": "Q11574",
        "label": "myriasecond",
        "siLabel": "second"
    },
    "Q1153426": {
        "factor": "0.0001803906837",
        "unit": "Q25517",
        "label": "G\u014d",
        "siLabel": "cubic metre"
    },
    "Q1158964": {
        "factor": "0.239",
        "unit": "Q25517",
        "label": "dan",
        "siLabel": "cubic metre"
    },
    "Q1164756": {
        "factor": "2",
        "unit": "Q25343",
        "label": "lane metre",
        "siLabel": "square metre"
    },
    "Q1165588": {
        "factor": "5.0292",
        "unit": "Q11573",
        "label": "rod",
        "siLabel": "metre"
    },
    "Q1165639": {
        "factor": "1",
        "unit": "Q89992008",
        "label": "daraf",
        "siLabel": "reciprocal farad"
    },
    "Q1165725": {
        "factor": "0.0000000000009869",
        "unit": "Q25343",
        "label": "darcy",
        "siLabel": "square metre"
    },
    "Q1165799": {
        "factor": "0.0000254",
        "unit": "Q11573",
        "label": "thou",
        "siLabel": "metre"
    },
    "Q1170886": {
        "factor": "9062.08",
        "unit": "Q11573",
        "label": "Saxon post mile",
        "siLabel": "metre"
    },
    "Q1172583": {
        "factor": "0.7112",
        "unit": "Q11573",
        "label": "arshin",
        "siLabel": "metre"
    },
    "Q1182218": {
        "factor": "0.01741458",
        "unit": "Q11573",
        "label": "dedo",
        "siLabel": "metre"
    },
    "Q1185752": {
        "factor": "109.09091",
        "unit": "Q11573",
        "label": "Ch\u014d",
        "siLabel": "metre"
    },
    "Q1194225": {
        "factor": "4.4482216152605",
        "unit": "Q12438",
        "label": "pound-force",
        "siLabel": "newton"
    },
    "Q1194852": {
        "factor": "1079252848800",
        "unit": "Q11573",
        "label": "light-hour",
        "siLabel": "metre"
    },
    "Q1196837": {
        "factor": "18549000000000000000000000000000000000000000",
        "unit": "Q1063756",
        "label": "Planck angular frequency",
        "siLabel": "radian per second"
    },
    "Q1196846": {
        "factor": "34790000000000000000000000",
        "unit": "Q25272",
        "label": "Planck current",
        "siLabel": "ampere"
    },
    "Q1197459": {
        "factor": "1000000",
        "unit": "Q11574",
        "label": "megasecond",
        "siLabel": "second"
    },
    "Q1242244": {
        "factor": "0.000250",
        "unit": "Q25517",
        "label": "cup",
        "siLabel": "cubic metre"
    },
    "Q1250769": {
        "factor": "9.290304",
        "unit": "Q25343",
        "label": "square",
        "siLabel": "square metre"
    },
    "Q1290875": {
        "factor": "0.001276",
        "unit": "Q25517",
        "label": "kab",
        "siLabel": "cubic metre"
    },
    "Q1322380": {
        "factor": "1000000000000",
        "unit": "Q11574",
        "label": "terasecond",
        "siLabel": "second"
    },
    "Q1323237": {
        "factor": "29.9792458",
        "unit": "Q47083",
        "label": "Planck impedance",
        "siLabel": "ohm"
    },
    "Q1323615": {
        "factor": "0.0311034768",
        "unit": "Q11570",
        "label": "troy ounce",
        "siLabel": "kilogram"
    },
    "Q1328525": {
        "factor": "17987547480",
        "unit": "Q11573",
        "label": "light-minute",
        "siLabel": "metre"
    },
    "Q1361854": {
        "factor": "0.00155517384",
        "unit": "Q11570",
        "label": "pennyweight",
        "siLabel": "kilogram"
    },
    "Q1363007": {
        "factor": "14.593903",
        "unit": "Q11570",
        "label": "slug",
        "siLabel": "kilogram"
    },
    "Q1374438": {
        "factor": "1000",
        "unit": "Q11574",
        "label": "kilosecond",
        "siLabel": "second"
    },
    "Q1377051": {
        "factor": "1000000000",
        "unit": "Q11574",
        "label": "gigasecond",
        "siLabel": "second"
    },
    "Q1377741": {
        "factor": "1042900000000000000000000000",
        "unit": "Q25250",
        "label": "Planck voltage",
        "siLabel": "volt"
    },
    "Q1380510": {
        "factor": "1000",
        "unit": "Q25343",
        "label": "maal",
        "siLabel": "square metre"
    },
    "Q1396128": {
        "factor": "96485.3399",
        "unit": "Q25406",
        "label": "faraday",
        "siLabel": "coulomb"
    },
    "Q1399533": {
        "factor": "0.019",
        "unit": "Q11573",
        "label": "digit",
        "siLabel": "metre"
    },
    "Q1399890": {
        "factor": "4200",
        "unit": "Q25343",
        "label": "feddan",
        "siLabel": "square metre"
    },
    "Q1400868": {
        "factor": "10000",
        "unit": "Q11570",
        "label": "vagon",
        "siLabel": "kilogram"
    },
    "Q1417229": {
        "factor": "0.0003183098861837906715377675267450287240689192914809128974953346881177935952684530701802276055325061719121456854535159160738",
        "unit": "Q281096",
        "label": "skot",
        "siLabel": "candela per square metre"
    },
    "Q1424298": {
        "factor": "0.4",
        "unit": "Q25517",
        "label": "queue",
        "siLabel": "cubic metre"
    },
    "Q1427899": {
        "factor": "0.04445",
        "unit": "Q11573",
        "label": "rack unit",
        "siLabel": "metre"
    },
    "Q1434123": {
        "factor": "0.0000035516328125",
        "unit": "Q25517",
        "label": "fluid dram",
        "siLabel": "cubic metre"
    },
    "Q1434381": {
        "factor": "0.00000000000000000000000001",
        "unit": "Q95375885",
        "label": "jansky",
        "siLabel": "watt per square metre hertz"
    },
    "Q1441459": {
        "factor": "1",
        "unit": "Q1441459",
        "label": "ohm metre",
        "siLabel": "ohm metre"
    },
    "Q1453450": {
        "factor": "6.916",
        "unit": "Q11570",
        "label": "gauting",
        "siLabel": "kilogram"
    },
    "Q1463969": {
        "factor": "1",
        "unit": "Q1463969",
        "label": "watt per metre kelvin",
        "siLabel": "watt per metre kelvin"
    },
    "Q1472674": {
        "factor": "0.0000000000001",
        "unit": "Q11574",
        "label": "svedberg",
        "siLabel": "second"
    },
    "Q1493191": {
        "factor": "0.000000001",
        "unit": "Q163343",
        "label": "gamma",
        "siLabel": "tesla"
    },
    "Q1501075": {
        "factor": "0.0009023",
        "unit": "Q25517",
        "label": "Gemet",
        "siLabel": "cubic metre"
    },
    "Q1515261": {
        "factor": "0.000001256637062",
        "unit": "Q21392882",
        "label": "vacuum permeability",
        "siLabel": "newton per square ampere"
    },
    "Q1520867": {
        "factor": "1728",
        "unit": "Q199",
        "label": "great gross",
        "siLabel": "1"
    },
    "Q1523859": {
        "factor": "0.024",
        "unit": "Q11573",
        "label": "Q1523859",
        "siLabel": "metre"
    },
    "Q1542309": {
        "factor": "0.000000000000100209952",
        "unit": "Q11573",
        "label": "X unit",
        "siLabel": "metre"
    },
    "Q1545979": {
        "factor": "0.02831685",
        "unit": "Q25517",
        "label": "cubic foot",
        "siLabel": "cubic metre"
    },
    "Q1547498": {
        "factor": "144",
        "unit": "Q199",
        "label": "gross",
        "siLabel": "1"
    },
    "Q1550511": {
        "factor": "0.8361274",
        "unit": "Q25343",
        "label": "square yard",
        "siLabel": "square metre"
    },
    "Q1552740": {
        "factor": "0.1016",
        "unit": "Q11573",
        "label": "hand",
        "siLabel": "metre"
    },
    "Q1569733": {
        "factor": "0.0001",
        "unit": "Q3332099",
        "label": "stokes",
        "siLabel": "square metre per second"
    },
    "Q1577757": {
        "factor": "0.201168",
        "unit": "Q11573",
        "label": "link",
        "siLabel": "metre"
    },
    "Q1578823": {
        "factor": "622080000",
        "unit": "Q11574",
        "label": "K'atun",
        "siLabel": "second"
    },
    "Q1585993": {
        "factor": "1",
        "unit": "Q25517",
        "label": "stere",
        "siLabel": "cubic metre"
    },
    "Q1630774": {
        "factor": "0.00225582938797796693538828201664",
        "unit": "Q11573",
        "label": "ligne",
        "siLabel": "metre"
    },
    "Q1637963": {
        "factor": "0.00000005919388388",
        "unit": "Q25517",
        "label": "minim",
        "siLabel": "cubic metre"
    },
    "Q1640501": {
        "factor": "9.80665",
        "unit": "Q11570",
        "label": "hyl",
        "siLabel": "kilogram"
    },
    "Q1645498": {
        "factor": "0.000000001",
        "unit": "Q11570",
        "label": "microgram",
        "siLabel": "kilogram"
    },
    "Q1645564": {
        "factor": "0.0246",
        "unit": "Q11573",
        "label": "uncia",
        "siLabel": "metre"
    },
    "Q1645966": {
        "factor": "185",
        "unit": "Q11573",
        "label": "stadion",
        "siLabel": "metre"
    },
    "Q1654435": {
        "factor": "0.007",
        "unit": "Q25250",
        "label": "IRE",
        "siLabel": "volt"
    },
    "Q1709783": {
        "factor": "1",
        "unit": "Q1709783",
        "label": "joule second",
        "siLabel": "joule second"
    },
    "Q1741429": {
        "factor": "9.80665",
        "unit": "Q215571",
        "label": "kilopondmetre",
        "siLabel": "newton metre"
    },
    "Q1768929": {
        "factor": "980.665",
        "unit": "Q25236",
        "label": "poncelet",
        "siLabel": "watt"
    },
    "Q1770733": {
        "factor": "1000000000",
        "unit": "Q11570",
        "label": "teragram",
        "siLabel": "kilogram"
    },
    "Q1772386": {
        "factor": "0.0001",
        "unit": "Q11570",
        "label": "decigram",
        "siLabel": "kilogram"
    },
    "Q1774323": {
        "factor": "1000",
        "unit": "Q11573",
        "label": "Klick",
        "siLabel": "metre"
    },
    "Q1777507": {
        "factor": "0.000000000000001",
        "unit": "Q11574",
        "label": "femtosecond",
        "siLabel": "second"
    },
    "Q1778552": {
        "factor": "86164.099",
        "unit": "Q11574",
        "label": "sidereal day",
        "siLabel": "second"
    },
    "Q1790901": {
        "factor": "846786664623715000000000000000000000000000000000",
        "unit": "Q25517",
        "label": "cubic light year",
        "siLabel": "cubic metre"
    },
    "Q1790908": {
        "factor": "4168181825",
        "unit": "Q25517",
        "label": "cubic mile",
        "siLabel": "cubic metre"
    },
    "Q1793863": {
        "factor": "1000",
        "unit": "Q12438",
        "label": "sth\u00e8ne",
        "siLabel": "newton"
    },
    "Q1798227": {
        "factor": "0.01745329251994329576923690768488612713",
        "unit": "Q33680",
        "label": "decimal degrees",
        "siLabel": "radian"
    },
    "Q1805331": {
        "factor": "41840",
        "unit": "Q80374519",
        "label": "langley",
        "siLabel": "joule per square metre"
    },
    "Q1815100": {
        "factor": "0.00001",
        "unit": "Q25517",
        "label": "centilitre",
        "siLabel": "cubic metre"
    },
    "Q1823150": {
        "factor": "0.000001",
        "unit": "Q25236",
        "label": "microwatt",
        "siLabel": "watt"
    },
    "Q1826195": {
        "factor": "0.0001",
        "unit": "Q25517",
        "label": "decilitre",
        "siLabel": "cubic metre"
    },
    "Q1872619": {
        "factor": "0.000000000000000000001",
        "unit": "Q11574",
        "label": "zeptosecond",
        "siLabel": "second"
    },
    "Q1897602": {
        "factor": "0.00004443494",
        "unit": "Q11570",
        "label": "dolia",
        "siLabel": "kilogram"
    },
    "Q1913097": {
        "factor": "0.000000000000000001",
        "unit": "Q11570",
        "label": "femtogram",
        "siLabel": "kilogram"
    },
    "Q1916026": {
        "factor": "0.000001",
        "unit": "Q25250",
        "label": "microvolt",
        "siLabel": "volt"
    },
    "Q1917076": {
        "factor": "0.83",
        "unit": "Q11573",
        "label": "megalithic yard",
        "siLabel": "metre"
    },
    "Q1931664": {
        "factor": "0.004266",
        "unit": "Q11570",
        "label": "zolotnik",
        "siLabel": "kilogram"
    },
    "Q1935515": {
        "factor": "0.001",
        "unit": "Q65665809",
        "label": "milliampere second",
        "siLabel": "ampere second"
    },
    "Q1936270": {
        "factor": "0.000017638",
        "unit": "Q11573",
        "label": "twip",
        "siLabel": "metre"
    },
    "Q1940373": {
        "factor": "0.013",
        "unit": "Q25517",
        "label": "omer",
        "siLabel": "cubic metre"
    },
    "Q1970718": {
        "factor": "10000",
        "unit": "Q11573",
        "label": "myriametre",
        "siLabel": "metre"
    },
    "Q1972579": {
        "factor": "0.138254954376",
        "unit": "Q12438",
        "label": "poundal",
        "siLabel": "newton"
    },
    "Q2002583": {
        "factor": "0.000015",
        "unit": "Q25517",
        "label": "tablespoon",
        "siLabel": "cubic metre"
    },
    "Q2018709": {
        "factor": "2.1336",
        "unit": "Q11573",
        "label": "sazhen",
        "siLabel": "metre"
    },
    "Q2029156": {
        "factor": "1055000000000000000",
        "unit": "Q25269",
        "label": "quad",
        "siLabel": "joule"
    },
    "Q2029519": {
        "factor": "0.1",
        "unit": "Q25517",
        "label": "hectolitre",
        "siLabel": "cubic metre"
    },
    "Q2042279": {
        "factor": "9806.65",
        "unit": "Q44395",
        "label": "metre of water",
        "siLabel": "pascal"
    },
    "Q2051195": {
        "factor": "3600000000000",
        "unit": "Q25269",
        "label": "gigawatt hour",
        "siLabel": "joule"
    },
    "Q2052385": {
        "factor": "0.03427725526",
        "unit": "Q25517",
        "label": "Q2052385",
        "siLabel": "cubic metre"
    },
    "Q2052387": {
        "factor": "0.00001983637",
        "unit": "Q25517",
        "label": "Parisian cubic inch",
        "siLabel": "cubic metre"
    },
    "Q2064166": {
        "factor": "10.764",
        "unit": "Q179836",
        "label": "foot-candle",
        "siLabel": "lux"
    },
    "Q2066484": {
        "factor": "299.792",
        "unit": "Q25250",
        "label": "statvolt",
        "siLabel": "volt"
    },
    "Q2080811": {
        "factor": "0.01",
        "unit": "Q199",
        "label": "volume percent",
        "siLabel": "1"
    },
    "Q2095762": {
        "factor": "1.7018",
        "unit": "Q11573",
        "label": "smoot",
        "siLabel": "metre"
    },
    "Q2099374": {
        "factor": "29.55",
        "unit": "Q11573",
        "label": "plethron",
        "siLabel": "metre"
    },
    "Q2100949": {
        "factor": "0.1",
        "unit": "Q21016931",
        "label": "poise",
        "siLabel": "pascal second"
    },
    "Q2118176": {
        "factor": "1478.7",
        "unit": "Q11573",
        "label": "milia passum",
        "siLabel": "metre"
    },
    "Q2121867": {
        "factor": "0.04445",
        "unit": "Q11573",
        "label": "vershok",
        "siLabel": "metre"
    },
    "Q2140397": {
        "factor": "0.000016387064",
        "unit": "Q25517",
        "label": "cubic inch",
        "siLabel": "cubic metre"
    },
    "Q2143992": {
        "factor": "1000",
        "unit": "Q39369",
        "label": "kilohertz",
        "siLabel": "hertz"
    },
    "Q2147412": {
        "factor": "10",
        "unit": "Q100293463",
        "label": "rhe",
        "siLabel": "reciprocal pascal second"
    },
    "Q2151240": {
        "factor": "10",
        "unit": "Q11570",
        "label": "myriagram",
        "siLabel": "kilogram"
    },
    "Q2165290": {
        "factor": "0.7645549",
        "unit": "Q25517",
        "label": "cubic yard",
        "siLabel": "cubic metre"
    },
    "Q2171489": {
        "factor": "747859.06685952",
        "unit": "Q25343",
        "label": "Rubbio",
        "siLabel": "square metre"
    },
    "Q2175964": {
        "factor": "0.001",
        "unit": "Q25517",
        "label": "cubic decimetre",
        "siLabel": "cubic metre"
    },
    "Q2193984": {
        "factor": "1728000",
        "unit": "Q11574",
        "label": "Uinic",
        "siLabel": "second"
    },
    "Q2208377": {
        "factor": "0.0005067075",
        "unit": "Q25343",
        "label": "circular inch",
        "siLabel": "square metre"
    },
    "Q2215478": {
        "factor": "0.000000000001",
        "unit": "Q199",
        "label": "parts per trillion",
        "siLabel": "1"
    },
    "Q2216184": {
        "factor": "0.092019",
        "unit": "Q25517",
        "label": "Salzmass",
        "siLabel": "cubic metre"
    },
    "Q2254856": {
        "factor": "1",
        "unit": "Q25343",
        "label": "centiare",
        "siLabel": "square metre"
    },
    "Q2269240": {
        "factor": "10368000",
        "unit": "Q11574",
        "label": "academic term",
        "siLabel": "second"
    },
    "Q2273801": {
        "factor": "0.012",
        "unit": "Q11570",
        "label": "Seron",
        "siLabel": "kilogram"
    },
    "Q2276380": {
        "factor": "745.7",
        "unit": "Q25236",
        "label": "imperial horsepower",
        "siLabel": "watt"
    },
    "Q2282891": {
        "factor": "0.000000001",
        "unit": "Q25517",
        "label": "microlitre",
        "siLabel": "cubic metre"
    },
    "Q2282906": {
        "factor": "0.000000000001",
        "unit": "Q11570",
        "label": "nanogram",
        "siLabel": "kilogram"
    },
    "Q2332346": {
        "factor": "0.000001",
        "unit": "Q25517",
        "label": "millilitre",
        "siLabel": "cubic metre"
    },
    "Q2347874": {
        "factor": "0.0762",
        "unit": "Q11573",
        "label": "palm",
        "siLabel": "metre"
    },
    "Q2397915": {
        "factor": "0.000254",
        "unit": "Q11573",
        "label": "tochka",
        "siLabel": "metre"
    },
    "Q2407803": {
        "factor": "0.000375972",
        "unit": "Q11573",
        "label": "Didot point",
        "siLabel": "metre"
    },
    "Q2415057": {
        "factor": "20",
        "unit": "Q199",
        "label": "score",
        "siLabel": "1"
    },
    "Q2415352": {
        "factor": "1",
        "unit": "Q2415352",
        "label": "mole per cubic metre",
        "siLabel": "mole per cubic metre"
    },
    "Q2438073": {
        "factor": "0.000000000000000000001",
        "unit": "Q11570",
        "label": "attogram",
        "siLabel": "kilogram"
    },
    "Q2448803": {
        "factor": "0.001",
        "unit": "Q25250",
        "label": "millivolt",
        "siLabel": "volt"
    },
    "Q2451296": {
        "factor": "0.000001",
        "unit": "Q131255",
        "label": "microfarad",
        "siLabel": "farad"
    },
    "Q2474258": {
        "factor": "0.001",
        "unit": "Q103246",
        "label": "millisievert",
        "siLabel": "sievert"
    },
    "Q2483628": {
        "factor": "0.000000000000000001",
        "unit": "Q11574",
        "label": "attosecond",
        "siLabel": "second"
    },
    "Q2489298": {
        "factor": "0.0001",
        "unit": "Q25343",
        "label": "square centimetre",
        "siLabel": "square metre"
    },
    "Q2490574": {
        "factor": "0.001",
        "unit": "Q25272",
        "label": "milliampere",
        "siLabel": "ampere"
    },
    "Q2518569": {
        "factor": "0.000000001",
        "unit": "Q103246",
        "label": "nanosievert",
        "siLabel": "sievert"
    },
    "Q2553708": {
        "factor": "1000000",
        "unit": "Q25250",
        "label": "megavolt",
        "siLabel": "volt"
    },
    "Q2554092": {
        "factor": "1000",
        "unit": "Q25250",
        "label": "kilovolt",
        "siLabel": "volt"
    },
    "Q2559410": {
        "factor": "0.00026",
        "unit": "Q25517",
        "label": "Kotyla",
        "siLabel": "cubic metre"
    },
    "Q2576687": {
        "factor": "0.0374",
        "unit": "Q25517",
        "label": "metretes",
        "siLabel": "cubic metre"
    },
    "Q2612219": {
        "factor": "1000000000000",
        "unit": "Q11570",
        "label": "petagram",
        "siLabel": "kilogram"
    },
    "Q2619500": {
        "factor": "100000000000000000000000000000000000000000000",
        "unit": "Q25269",
        "label": "foe",
        "siLabel": "joule"
    },
    "Q2630196": {
        "factor": "0.0000000982",
        "unit": "Q103246",
        "label": "banana equivalent dose",
        "siLabel": "sievert"
    },
    "Q2636421": {
        "factor": "0.000000001",
        "unit": "Q163354",
        "label": "nanohenry",
        "siLabel": "henry"
    },
    "Q2637946": {
        "factor": "0.01",
        "unit": "Q25517",
        "label": "decalitre",
        "siLabel": "cubic metre"
    },
    "Q2652700": {
        "factor": "1",
        "unit": "Q41509",
        "label": "osmole",
        "siLabel": "mole"
    },
    "Q2655272": {
        "factor": "1000000000000000",
        "unit": "Q11570",
        "label": "exagram",
        "siLabel": "kilogram"
    },
    "Q2659078": {
        "factor": "3600000000000000",
        "unit": "Q25269",
        "label": "terawatt hour",
        "siLabel": "joule"
    },
    "Q2679083": {
        "factor": "0.000001",
        "unit": "Q163354",
        "label": "microhenry",
        "siLabel": "henry"
    },
    "Q2682463": {
        "factor": "0.000000001",
        "unit": "Q131255",
        "label": "nanofarad",
        "siLabel": "farad"
    },
    "Q2691798": {
        "factor": "0.00001",
        "unit": "Q11570",
        "label": "centigram",
        "siLabel": "kilogram"
    },
    "Q2718629": {
        "factor": "0.0042333",
        "unit": "Q11573",
        "label": "pica",
        "siLabel": "metre"
    },
    "Q2723404": {
        "factor": "31558196.01312",
        "unit": "Q11574",
        "label": "Gaussian year",
        "siLabel": "second"
    },
    "Q2737347": {
        "factor": "0.000001",
        "unit": "Q25343",
        "label": "square millimetre",
        "siLabel": "square metre"
    },
    "Q2738821": {
        "factor": "25902068371200",
        "unit": "Q11573",
        "label": "light-day",
        "siLabel": "metre"
    },
    "Q2739114": {
        "factor": "0.000001",
        "unit": "Q103246",
        "label": "microsievert",
        "siLabel": "sievert"
    },
    "Q2756030": {
        "factor": "0.000000000001",
        "unit": "Q131255",
        "label": "picofarad",
        "siLabel": "farad"
    },
    "Q2762458": {
        "factor": "0.000000000000000000000001",
        "unit": "Q11574",
        "label": "yoctosecond",
        "siLabel": "second"
    },
    "Q2781048": {
        "factor": "1000",
        "unit": "Q83216",
        "label": "kilocandela",
        "siLabel": "candela"
    },
    "Q2793566": {
        "factor": "1000000000",
        "unit": "Q25250",
        "label": "gigavolt",
        "siLabel": "volt"
    },
    "Q2799294": {
        "factor": "1000000",
        "unit": "Q11570",
        "label": "gigagram",
        "siLabel": "kilogram"
    },
    "Q2844434": {
        "factor": "0.03939",
        "unit": "Q25517",
        "label": "amphora",
        "siLabel": "cubic metre"
    },
    "Q2844477": {
        "factor": "1",
        "unit": "Q2844477",
        "label": "ampere per square metre",
        "siLabel": "ampere per square metre"
    },
    "Q2844478": {
        "factor": "1",
        "unit": "Q2844478",
        "label": "ampere per metre",
        "siLabel": "ampere per metre"
    },
    "Q2880682": {
        "factor": "0.278635",
        "unit": "Q11573",
        "label": "Spanish foot",
        "siLabel": "metre"
    },
    "Q2924137": {
        "factor": "0.001",
        "unit": "Q163354",
        "label": "millihenry",
        "siLabel": "henry"
    },
    "Q2936398": {
        "factor": "1.555",
        "unit": "Q11573",
        "label": "cana",
        "siLabel": "metre"
    },
    "Q2981070": {
        "factor": "0.001",
        "unit": "Q83216",
        "label": "millicandela",
        "siLabel": "candela"
    },
    "Q2993680": {
        "factor": "1209600",
        "unit": "Q11574",
        "label": "fortnight",
        "siLabel": "second"
    },
    "Q3022468": {
        "factor": "0.0012739",
        "unit": "Q11570",
        "label": "denier",
        "siLabel": "kilogram"
    },
    "Q3085309": {
        "factor": "1",
        "unit": "Q3085309",
        "label": "joule per kilogram kelvin",
        "siLabel": "joule per kilogram kelvin"
    },
    "Q3117809": {
        "factor": "0.000001",
        "unit": "Q25272",
        "label": "microampere",
        "siLabel": "ampere"
    },
    "Q3186734": {
        "factor": "1",
        "unit": "Q3186734",
        "label": "joule per cubic metre kelvin",
        "siLabel": "joule per cubic metre kelvin"
    },
    "Q3194571": {
        "factor": "864",
        "unit": "Q11574",
        "label": "ke",
        "siLabel": "second"
    },
    "Q3194958": {
        "factor": "1",
        "unit": "Q3194958",
        "label": "kelvin per watt",
        "siLabel": "kelvin per watt"
    },
    "Q3195007": {
        "factor": "1.8181818181818181818181818181818181818181818181818181818181818181818181818181818181818181818181818181818181818181818181818182",
        "unit": "Q11573",
        "label": "ken",
        "siLabel": "metre"
    },
    "Q3207456": {
        "factor": "0.001",
        "unit": "Q25236",
        "label": "milliwatt",
        "siLabel": "watt"
    },
    "Q3221356": {
        "factor": "0.000000000000000000000001",
        "unit": "Q11573",
        "label": "yoctometre",
        "siLabel": "metre"
    },
    "Q3239557": {
        "factor": "0.000000000000001",
        "unit": "Q11570",
        "label": "picogram",
        "siLabel": "kilogram"
    },
    "Q3241121": {
        "factor": "0.000001",
        "unit": "Q11570",
        "label": "milligram",
        "siLabel": "kilogram"
    },
    "Q3249364": {
        "factor": "0.01",
        "unit": "Q11574",
        "label": "centisecond",
        "siLabel": "second"
    },
    "Q3251645": {
        "factor": "0.1",
        "unit": "Q11574",
        "label": "decisecond",
        "siLabel": "second"
    },
    "Q3267417": {
        "factor": "1000000000000",
        "unit": "Q11573",
        "label": "terametre",
        "siLabel": "metre"
    },
    "Q3270676": {
        "factor": "0.000000000000000000001",
        "unit": "Q11573",
        "label": "zeptometre",
        "siLabel": "metre"
    },
    "Q3276763": {
        "factor": "1000000000",
        "unit": "Q39369",
        "label": "gigahertz",
        "siLabel": "hertz"
    },
    "Q3277907": {
        "factor": "1000000000000000000",
        "unit": "Q11573",
        "label": "exametre",
        "siLabel": "metre"
    },
    "Q3277915": {
        "factor": "1000000000000000000000",
        "unit": "Q11573",
        "label": "zettametre",
        "siLabel": "metre"
    },
    "Q3277919": {
        "factor": "1000000000000000",
        "unit": "Q11573",
        "label": "petametre",
        "siLabel": "metre"
    },
    "Q3312063": {
        "factor": "0.000000000000000001",
        "unit": "Q25517",
        "label": "femtolitre",
        "siLabel": "cubic metre"
    },
    "Q3320608": {
        "factor": "1000",
        "unit": "Q25236",
        "label": "kilowatt",
        "siLabel": "watt"
    },
    "Q3331719": {
        "factor": "0.01",
        "unit": "Q25343",
        "label": "square decimetre",
        "siLabel": "square metre"
    },
    "Q3332092": {
        "factor": "1",
        "unit": "Q3332092",
        "label": "square metre kelvin per watt",
        "siLabel": "square metre kelvin per watt"
    },
    "Q3332095": {
        "factor": "1",
        "unit": "Q3332095",
        "label": "cubic metre per kilogram",
        "siLabel": "cubic metre per kilogram"
    },
    "Q3332099": {
        "factor": "1",
        "unit": "Q3332099",
        "label": "square metre per second",
        "siLabel": "square metre per second"
    },
    "Q3332689": {
        "factor": "3517",
        "unit": "Q25236",
        "label": "Ton of refrigeration",
        "siLabel": "watt"
    },
    "Q3332822": {
        "factor": "4184000000000000",
        "unit": "Q25269",
        "label": "megaton of TNT",
        "siLabel": "joule"
    },
    "Q3348257": {
        "factor": "0.00072",
        "unit": "Q11570",
        "label": "Greek obolus",
        "siLabel": "kilogram"
    },
    "Q3356258": {
        "factor": "1.851",
        "unit": "Q11573",
        "label": "orgyia",
        "siLabel": "metre"
    },
    "Q3395194": {
        "factor": "1",
        "unit": "Q3395194",
        "label": "newton second",
        "siLabel": "newton second"
    },
    "Q3396758": {
        "factor": "1000",
        "unit": "Q25343",
        "label": "decare",
        "siLabel": "square metre"
    },
    "Q3421309": {
        "factor": "69911000",
        "unit": "Q11573",
        "label": "Jupiter radius",
        "siLabel": "metre"
    },
    "Q3495543": {
        "factor": "100",
        "unit": "Q44395",
        "label": "millibar",
        "siLabel": "pascal"
    },
    "Q3499846": {
        "factor": "164",
        "unit": "Q11570",
        "label": "berkovets",
        "siLabel": "kilogram"
    },
    "Q3562962": {
        "factor": "1",
        "unit": "Q3562962",
        "label": "volt per metre",
        "siLabel": "volt per metre"
    },
    "Q3565837": {
        "factor": "0.0389",
        "unit": "Q25517",
        "label": "bath",
        "siLabel": "cubic metre"
    },
    "Q3566737": {
        "factor": "1",
        "unit": "Q3566737",
        "label": "watt per square metre",
        "siLabel": "watt per square metre"
    },
    "Q3566738": {
        "factor": "1",
        "unit": "Q3566738",
        "label": "watt per square metre kelvin",
        "siLabel": "watt per square metre kelvin"
    },
    "Q3617326": {
        "factor": "0.4251",
        "unit": "Q11570",
        "label": "sk\u00e5lpund",
        "siLabel": "kilogram"
    },
    "Q3646719": {
        "factor": "0.00323",
        "unit": "Q25517",
        "label": "congius",
        "siLabel": "cubic metre"
    },
    "Q3674704": {
        "factor": "1000",
        "unit": "Q182429",
        "label": "kilometre per second",
        "siLabel": "metre per second"
    },
    "Q3675550": {
        "factor": "0.000000001",
        "unit": "Q25517",
        "label": "cubic millimetre",
        "siLabel": "cubic metre"
    },
    "Q3730828": {
        "factor": "2700",
        "unit": "Q25343",
        "label": "arura",
        "siLabel": "square metre"
    },
    "Q3744908": {
        "factor": "0.00123",
        "unit": "Q25517",
        "label": "shtof",
        "siLabel": "cubic metre"
    },
    "Q3773454": {
        "factor": "30856775810000000000000",
        "unit": "Q11573",
        "label": "megaparsec",
        "siLabel": "metre"
    },
    "Q3774493": {
        "factor": "0.2957",
        "unit": "Q11573",
        "label": "pes",
        "siLabel": "metre"
    },
    "Q3774562": {
        "factor": "647497.027584",
        "unit": "Q25343",
        "label": "homestead",
        "siLabel": "square metre"
    },
    "Q3785200": {
        "factor": "5036",
        "unit": "Q25343",
        "label": "heredium",
        "siLabel": "square metre"
    },
    "Q3858002": {
        "factor": "3.6",
        "unit": "Q25406",
        "label": "milliampere hour",
        "siLabel": "coulomb"
    },
    "Q3867152": {
        "factor": "0.3048",
        "unit": "Q1051665",
        "label": "foot per square second",
        "siLabel": "metre per square second"
    },
    "Q3894667": {
        "factor": "900",
        "unit": "Q11574",
        "label": "quarter of an hour",
        "siLabel": "second"
    },
    "Q3902688": {
        "factor": "0.000000000000001",
        "unit": "Q25517",
        "label": "picolitre",
        "siLabel": "cubic metre"
    },
    "Q3902709": {
        "factor": "0.000000000001",
        "unit": "Q11574",
        "label": "picosecond",
        "siLabel": "second"
    },
    "Q3953133": {
        "factor": "0.001295982",
        "unit": "Q11570",
        "label": "scruple",
        "siLabel": "kilogram"
    },
    "Q3972226": {
        "factor": "1",
        "unit": "Q25517",
        "label": "kilolitre",
        "siLabel": "cubic metre"
    },
    "Q4006278": {
        "factor": "0.023",
        "unit": "Q11570",
        "label": "Uqiyya",
        "siLabel": "kilogram"
    },
    "Q4041686": {
        "factor": "248.84",
        "unit": "Q44395",
        "label": "inch of water",
        "siLabel": "pascal"
    },
    "Q4068266": {
        "factor": "0.003732",
        "unit": "Q11570",
        "label": "apothecaries' drachm",
        "siLabel": "kilogram"
    },
    "Q4080926": {
        "factor": "1.022",
        "unit": "Q11570",
        "label": "besmen",
        "siLabel": "kilogram"
    },
    "Q4176683": {
        "factor": "10",
        "unit": "Q25406",
        "label": "abcoulomb",
        "siLabel": "coulomb"
    },
    "Q4206051": {
        "factor": "162.146",
        "unit": "Q11570",
        "label": "Yuk",
        "siLabel": "kilogram"
    },
    "Q4243638": {
        "factor": "1000000000",
        "unit": "Q25517",
        "label": "cubic kilometre",
        "siLabel": "cubic metre"
    },
    "Q4347344": {
        "factor": "2",
        "unit": "Q11573",
        "label": "Wa",
        "siLabel": "metre"
    },
    "Q4347407": {
        "factor": "4",
        "unit": "Q25343",
        "label": "Tarang wa",
        "siLabel": "square metre"
    },
    "Q4389960": {
        "factor": "3.0303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303030303",
        "unit": "Q11573",
        "label": "j\u014d",
        "siLabel": "metre"
    },
    "Q4406458": {
        "factor": "4976640000000",
        "unit": "Q11574",
        "label": "calabtun",
        "siLabel": "second"
    },
    "Q4443074": {
        "factor": "0.325",
        "unit": "Q11573",
        "label": "stopa",
        "siLabel": "metre"
    },
    "Q4456994": {
        "factor": "0.001",
        "unit": "Q131255",
        "label": "millifarad",
        "siLabel": "farad"
    },
    "Q4514998": {
        "factor": "0.1778",
        "unit": "Q11573",
        "label": "chetvert",
        "siLabel": "metre"
    },
    "Q4580949": {
        "factor": "0.00425",
        "unit": "Q11570",
        "label": "ort",
        "siLabel": "kilogram"
    },
    "Q4667368": {
        "factor": "0.000000001",
        "unit": "Q163354",
        "label": "abhenry",
        "siLabel": "henry"
    },
    "Q4668106": {
        "factor": "1000000000",
        "unit": "Q169893",
        "label": "abmho",
        "siLabel": "siemens"
    },
    "Q4674697": {
        "factor": "100000",
        "unit": "Q87047886",
        "label": "Acoustic ohm",
        "siLabel": "pascal second per cubic metre"
    },
    "Q4691480": {
        "factor": "0.00181",
        "unit": "Q11573",
        "label": "agate",
        "siLabel": "metre"
    },
    "Q4796294": {
        "factor": "0.459",
        "unit": "Q11570",
        "label": "arr\u00e1tel",
        "siLabel": "kilogram"
    },
    "Q4861171": {
        "factor": "0.0085",
        "unit": "Q11573",
        "label": "barleycorn",
        "siLabel": "metre"
    },
    "Q4940098": {
        "factor": "35",
        "unit": "Q11573",
        "label": "bolt",
        "siLabel": "metre"
    },
    "Q4968003": {
        "factor": "0.0000000318309886183790671537767526745028724068919291480912897495334688117793595268453070180227605532506171912145685453515916",
        "unit": "Q281096",
        "label": "bril",
        "siLabel": "candela per square metre"
    },
    "Q4989854": {
        "factor": "1000",
        "unit": "Q25269",
        "label": "kilojoule",
        "siLabel": "joule"
    },
    "Q4992853": {
        "factor": "4184000000000",
        "unit": "Q25269",
        "label": "kiloton of TNT",
        "siLabel": "joule"
    },
    "Q5121670": {
        "factor": "0.0000000005067075",
        "unit": "Q25343",
        "label": "circular mil",
        "siLabel": "square metre"
    },
    "Q5139563": {
        "factor": "100",
        "unit": "Q44395",
        "label": "hectopascal",
        "siLabel": "pascal"
    },
    "Q5181875": {
        "factor": "0.17",
        "unit": "Q25517",
        "label": "Cran",
        "siLabel": "cubic metre"
    },
    "Q5195628": {
        "factor": "1000000",
        "unit": "Q25517",
        "label": "cubic hectometre",
        "siLabel": "cubic metre"
    },
    "Q5196162": {
        "factor": "0.028316847",
        "unit": "Q794261",
        "label": "cubic foot per second",
        "siLabel": "cubic metre per second"
    },
    "Q5198171": {
        "factor": "1",
        "unit": "Q39369",
        "label": "cycle per second",
        "siLabel": "hertz"
    },
    "Q5198770": {
        "factor": "1000",
        "unit": "Q25517",
        "label": "cubic decametre",
        "siLabel": "cubic metre"
    },
    "Q5263280": {
        "factor": "4184000000000000000000",
        "unit": "Q25269",
        "label": "teraton of TNT",
        "siLabel": "joule"
    },
    "Q5309589": {
        "factor": "0.00440488",
        "unit": "Q25517",
        "label": "dry gallon",
        "siLabel": "cubic metre"
    },
    "Q5409016": {
        "factor": "1000000",
        "unit": "Q550341",
        "label": "megavolt ampere",
        "siLabel": "volt ampere"
    },
    "Q5465723": {
        "factor": "0.0421401100938048",
        "unit": "Q25269",
        "label": "foot-poundal",
        "siLabel": "joule"
    },
    "Q5465726": {
        "factor": "3.4262590996353905269167459616502185942345836205242895980081457842261522902636239909934874631928747639705405275598722719276552",
        "unit": "Q281096",
        "label": "foot-lambert",
        "siLabel": "candela per square metre"
    },
    "Q5503151": {
        "factor": "1000000000000",
        "unit": "Q39369",
        "label": "Fresnel",
        "siLabel": "hertz"
    },
    "Q5548818": {
        "factor": "0.00057",
        "unit": "Q11570",
        "label": "gerah",
        "siLabel": "kilogram"
    },
    "Q5564114": {
        "factor": "57.15",
        "unit": "Q11573",
        "label": "Girah",
        "siLabel": "metre"
    },
    "Q5610850": {
        "factor": "203",
        "unit": "Q25343",
        "label": "ground",
        "siLabel": "square metre"
    },
    "Q5619428": {
        "factor": "101.171",
        "unit": "Q25343",
        "label": "gunta",
        "siLabel": "square metre"
    },
    "Q5696515": {
        "factor": "100000000",
        "unit": "Q25343",
        "label": "Hectad",
        "siLabel": "square metre"
    },
    "Q5711261": {
        "factor": "0.000000000000000000000000000000000000000000000000000001",
        "unit": "Q25517",
        "label": "cubic attometre",
        "siLabel": "cubic metre"
    },
    "Q5790214": {
        "factor": "0.104365",
        "unit": "Q11573",
        "label": "Q5790214",
        "siLabel": "metre"
    },
    "Q5835793": {
        "factor": "898.456",
        "unit": "Q25343",
        "label": "robada",
        "siLabel": "square metre"
    },
    "Q5879479": {
        "factor": "1000000000",
        "unit": "Q25236",
        "label": "gigawatt",
        "siLabel": "watt"
    },
    "Q5901295": {
        "factor": "0.03605",
        "unit": "Q25343",
        "label": "hoppus",
        "siLabel": "square metre"
    },
    "Q5999460": {
        "factor": "528.42",
        "unit": "Q25343",
        "label": "marjal",
        "siLabel": "square metre"
    },
    "Q6003257": {
        "factor": "0.000000000000000001",
        "unit": "Q11573",
        "label": "attometre",
        "siLabel": "metre"
    },
    "Q6009164": {
        "factor": "3600000000",
        "unit": "Q25269",
        "label": "megawatt hour",
        "siLabel": "joule"
    },
    "Q6014364": {
        "factor": "0.0254",
        "unit": "Q182429",
        "label": "inch per second",
        "siLabel": "metre per second"
    },
    "Q6034654": {
        "factor": "0.65",
        "unit": "Q11573",
        "label": "Endaze",
        "siLabel": "metre"
    },
    "Q6059704": {
        "factor": "0.0001259",
        "unit": "Q25517",
        "label": "panilla",
        "siLabel": "cubic metre"
    },
    "Q6137407": {
        "factor": "1",
        "unit": "Q6137407",
        "label": "reciprocal second",
        "siLabel": "reciprocal second"
    },
    "Q6144634": {
        "factor": "0.05715",
        "unit": "Q11573",
        "label": "nail",
        "siLabel": "metre"
    },
    "Q6145487": {
        "factor": "864000",
        "unit": "Q11574",
        "label": "xun",
        "siLabel": "second"
    },
    "Q6170164": {
        "factor": "0.000000000000000000000000001",
        "unit": "Q11570",
        "label": "yoctogram",
        "siLabel": "kilogram"
    },
    "Q6171168": {
        "factor": "0.000000000000000000000001",
        "unit": "Q11570",
        "label": "zeptogram",
        "siLabel": "kilogram"
    },
    "Q6390907": {
        "factor": "0.01818436",
        "unit": "Q25517",
        "label": "kenning",
        "siLabel": "cubic metre"
    },
    "Q6408112": {
        "factor": "4184",
        "unit": "Q13035094",
        "label": "Kilocalorie per mole",
        "siLabel": "joule per mole"
    },
    "Q6408129": {
        "factor": "0.001",
        "unit": "Q11547251",
        "label": "kilometre per square kilometre",
        "siLabel": "reciprocal metre"
    },
    "Q6414556": {
        "factor": "4448.2216",
        "unit": "Q12438",
        "label": "kip",
        "siLabel": "newton"
    },
    "Q6502030": {
        "factor": "0.5",
        "unit": "Q11573",
        "label": "cubit",
        "siLabel": "metre"
    },
    "Q6502423": {
        "factor": "1.8288",
        "unit": "Q11573",
        "label": "fathom",
        "siLabel": "metre"
    },
    "Q6517513": {
        "factor": "0.01",
        "unit": "Q11570",
        "label": "decagram",
        "siLabel": "kilogram"
    },
    "Q6667379": {
        "factor": "6.096",
        "unit": "Q11573",
        "label": "rope",
        "siLabel": "metre"
    },
    "Q6824322": {
        "factor": "0.3",
        "unit": "Q11573",
        "label": "basic module",
        "siLabel": "metre"
    },
    "Q6824325": {
        "factor": "1500",
        "unit": "Q11573",
        "label": "Metric mile",
        "siLabel": "metre"
    },
    "Q6859652": {
        "factor": "133.3223684211",
        "unit": "Q44395",
        "label": "millimetre of mercury",
        "siLabel": "pascal"
    },
    "Q6961037": {
        "factor": "180",
        "unit": "Q11573",
        "label": "Nalva",
        "siLabel": "metre"
    },
    "Q6982035": {
        "factor": "1000000",
        "unit": "Q25236",
        "label": "megawatt",
        "siLabel": "watt"
    },
    "Q7038548": {
        "factor": "8",
        "unit": "Q11570",
        "label": "Ritil",
        "siLabel": "kilogram"
    },
    "Q7061741": {
        "factor": "2.4",
        "unit": "Q11573",
        "label": "horse length",
        "siLabel": "metre"
    },
    "Q7137383": {
        "factor": "0.027",
        "unit": "Q11573",
        "label": "Paris inch",
        "siLabel": "metre"
    },
    "Q7235735": {
        "factor": "0.2957",
        "unit": "Q11573",
        "label": "pous",
        "siLabel": "metre"
    },
    "Q7462601": {
        "factor": "0.00000001",
        "unit": "Q11574",
        "label": "shake",
        "siLabel": "second"
    },
    "Q7574000": {
        "factor": "12.5664",
        "unit": "Q177612",
        "label": "spat",
        "siLabel": "steradian"
    },
    "Q7616207": {
        "factor": "0.0508",
        "unit": "Q11573",
        "label": "stick",
        "siLabel": "metre"
    },
    "Q7672057": {
        "factor": "0.001024",
        "unit": "Q11574",
        "label": "TU",
        "siLabel": "second"
    },
    "Q7974907": {
        "factor": "3600",
        "unit": "Q57175225",
        "label": "watt-hour per kilogram",
        "siLabel": "joule per kilogram"
    },
    "Q7974920": {
        "factor": "1",
        "unit": "Q7974920",
        "label": "watt second",
        "siLabel": "watt second"
    },
    "Q7980400": {
        "factor": "0.000000000000000000000001853",
        "unit": "Q21088638",
        "label": "Weiss magneton",
        "siLabel": "joule per tesla"
    },
    "Q10317923": {
        "factor": "0.323",
        "unit": "Q11570",
        "label": "libra",
        "siLabel": "kilogram"
    },
    "Q10366756": {
        "factor": "60",
        "unit": "Q11570",
        "label": "Saca",
        "siLabel": "kilogram"
    },
    "Q10380431": {
        "factor": "1000000000000",
        "unit": "Q25269",
        "label": "terajoule",
        "siLabel": "joule"
    },
    "Q10397574": {
        "factor": "900",
        "unit": "Q11570",
        "label": "air-dry tonne",
        "siLabel": "kilogram"
    },
    "Q10543042": {
        "factor": "1000000000000000000000000",
        "unit": "Q11573",
        "label": "yottametre",
        "siLabel": "metre"
    },
    "Q10705671": {
        "factor": "0.024",
        "unit": "Q25517",
        "label": "Tr\u00f6",
        "siLabel": "cubic metre"
    },
    "Q10711818": {
        "factor": "3600",
        "unit": "Q104628312",
        "label": "VArh",
        "siLabel": "volt-ampere-reactive second"
    },
    "Q10748296": {
        "factor": "0.15482",
        "unit": "Q3332092",
        "label": "Clo",
        "siLabel": "square metre kelvin per watt"
    },
    "Q11034997": {
        "factor": "86400",
        "unit": "Q11574",
        "label": "nychthemeron",
        "siLabel": "second"
    },
    "Q11061003": {
        "factor": "0.000000000001",
        "unit": "Q25343",
        "label": "square micrometre",
        "siLabel": "square metre"
    },
    "Q11061005": {
        "factor": "0.000000000000000001",
        "unit": "Q25343",
        "label": "square nanometre",
        "siLabel": "square metre"
    },
    "Q11410513": {
        "factor": "991.736",
        "unit": "Q25343",
        "label": "tan",
        "siLabel": "square metre"
    },
    "Q11458676": {
        "factor": "1.515",
        "unit": "Q11573",
        "label": "Hiro",
        "siLabel": "metre"
    },
    "Q11481737": {
        "factor": "0.378",
        "unit": "Q11573",
        "label": "Q11481737",
        "siLabel": "metre"
    },
    "Q11491445": {
        "factor": "0.000010",
        "unit": "Q11573",
        "label": "\u5ffd",
        "siLabel": "metre"
    },
    "Q11547251": {
        "factor": "1",
        "unit": "Q11547251",
        "label": "reciprocal metre",
        "siLabel": "reciprocal metre"
    },
    "Q11687668": {
        "factor": "0.00571",
        "unit": "Q11570",
        "label": "bekah",
        "siLabel": "kilogram"
    },
    "Q11776930": {
        "factor": "1000",
        "unit": "Q11570",
        "label": "megagram",
        "siLabel": "kilogram"
    },
    "Q11781239": {
        "factor": "0.01",
        "unit": "Q844211",
        "label": "milligram per cent",
        "siLabel": "kilogram per cubic metre"
    },
    "Q11830636": {
        "factor": "47.8802589804",
        "unit": "Q44395",
        "label": "Psf",
        "siLabel": "pascal"
    },
    "Q11906933": {
        "factor": "23325",
        "unit": "Q11573",
        "label": "aspi",
        "siLabel": "metre"
    },
    "Q11925390": {
        "factor": "0.00027",
        "unit": "Q25517",
        "label": "hemina",
        "siLabel": "cubic metre"
    },
    "Q11929860": {
        "factor": "30856775814913700000",
        "unit": "Q11573",
        "label": "kiloparsec",
        "siLabel": "metre"
    },
    "Q11941352": {
        "factor": "0.000235",
        "unit": "Q25517",
        "label": "Q11941352",
        "siLabel": "cubic metre"
    },
    "Q11944169": {
        "factor": "0.02586",
        "unit": "Q25517",
        "label": "amphora quadrantal",
        "siLabel": "cubic metre"
    },
    "Q11982285": {
        "factor": "1000000000000000000000000000000000000000000000000000000",
        "unit": "Q25517",
        "label": "cubic exametre",
        "siLabel": "cubic metre"
    },
    "Q11982288": {
        "factor": "1000000000000000000000000000000000000000000000000000000000000000",
        "unit": "Q25517",
        "label": "cubic zettametre",
        "siLabel": "cubic metre"
    },
    "Q11982289": {
        "factor": "1000000000000000000000000000000000000",
        "unit": "Q25517",
        "label": "cubic terametre",
        "siLabel": "cubic metre"
    },
    "Q11982705": {
        "factor": "0.00332",
        "unit": "Q11570",
        "label": "kvintin",
        "siLabel": "kilogram"
    },
    "Q11995396": {
        "factor": "1000000000000",
        "unit": "Q25517",
        "label": "petalitre",
        "siLabel": "cubic metre"
    },
    "Q12011178": {
        "factor": "1000000000000000000000",
        "unit": "Q11574",
        "label": "zettasecond",
        "siLabel": "second"
    },
    "Q12048378": {
        "factor": "0.000242",
        "unit": "Q25517",
        "label": "Q12048378",
        "siLabel": "cubic metre"
    },
    "Q12122300": {
        "factor": "2133.6",
        "unit": "Q11573",
        "label": "border versta",
        "siLabel": "metre"
    },
    "Q12170198": {
        "factor": "3.3333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333333",
        "unit": "Q11573",
        "label": "zh\u00e0ng",
        "siLabel": "metre"
    },
    "Q12307606": {
        "factor": "7532.48",
        "unit": "Q11573",
        "label": "Danish mile",
        "siLabel": "metre"
    },
    "Q12307609": {
        "factor": "1851.11",
        "unit": "Q11573",
        "label": "Danish nautical mile",
        "siLabel": "metre"
    },
    "Q12492466": {
        "factor": "24191",
        "unit": "Q11570",
        "label": "Koyan",
        "siLabel": "kilogram"
    },
    "Q12495902": {
        "factor": "32.774128",
        "unit": "Q794261",
        "label": "million standard cubic feet per day",
        "siLabel": "cubic metre per second"
    },
    "Q12714022": {
        "factor": "45.35924",
        "unit": "Q11570",
        "label": "short hundredweight",
        "siLabel": "kilogram"
    },
    "Q12783919": {
        "factor": "1000000000",
        "unit": "Q131255",
        "label": "abfarad",
        "siLabel": "farad"
    },
    "Q12789864": {
        "factor": "0.000000000160217656535",
        "unit": "Q25269",
        "label": "gigaelectronvolt",
        "siLabel": "joule"
    },
    "Q12803163": {
        "factor": "0.02134",
        "unit": "Q11573",
        "label": "sotka",
        "siLabel": "metre"
    },
    "Q12818655": {
        "factor": "0.006",
        "unit": "Q25517",
        "label": "Ashir",
        "siLabel": "cubic metre"
    },
    "Q12818657": {
        "factor": "39.9",
        "unit": "Q11573",
        "label": "Ashl",
        "siLabel": "metre"
    },
    "Q12823177": {
        "factor": "0.336",
        "unit": "Q11570",
        "label": "Ilcha",
        "siLabel": "kilogram"
    },
    "Q12831634": {
        "factor": "11.6",
        "unit": "Q11570",
        "label": "Vayba",
        "siLabel": "kilogram"
    },
    "Q12831966": {
        "factor": "0.00033766",
        "unit": "Q11570",
        "label": "Vol",
        "siLabel": "kilogram"
    },
    "Q12874593": {
        "factor": "3600",
        "unit": "Q25269",
        "label": "watt hour",
        "siLabel": "joule"
    },
    "Q12955189": {
        "factor": "0.115274",
        "unit": "Q25517",
        "label": "Sach",
        "siLabel": "cubic metre"
    },
    "Q12955440": {
        "factor": "898755200000",
        "unit": "Q163354",
        "label": "stathenry",
        "siLabel": "henry"
    },
    "Q13035094": {
        "factor": "1",
        "unit": "Q13035094",
        "label": "joule per mole",
        "siLabel": "joule per mole"
    },
    "Q13139695": {
        "factor": "0.3048",
        "unit": "Q11573",
        "label": "Q13139695",
        "siLabel": "metre"
    },
    "Q13147228": {
        "factor": "1000",
        "unit": "Q844211",
        "label": "gram per cubic centimetre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q13400897": {
        "factor": "9.80665",
        "unit": "Q1051665",
        "label": "standard gravity",
        "siLabel": "metre per square second"
    },
    "Q13479685": {
        "factor": "9.80665",
        "unit": "Q44395",
        "label": "millimetre of water",
        "siLabel": "pascal"
    },
    "Q13530508": {
        "factor": "4444.4",
        "unit": "Q11573",
        "label": "league",
        "siLabel": "metre"
    },
    "Q13548586": {
        "factor": "1000000000000",
        "unit": "Q39369",
        "label": "terahertz",
        "siLabel": "hertz"
    },
    "Q13582667": {
        "factor": "98066.5",
        "unit": "Q44395",
        "label": "kilogram-force per square centimetre",
        "siLabel": "pascal"
    },
    "Q14158377": {
        "factor": "0.0000000000000000000000000000000000000000000000000000000000000000000002612",
        "unit": "Q25343",
        "label": "Planck area",
        "siLabel": "square metre"
    },
    "Q14333713": {
        "factor": "0.000546",
        "unit": "Q25517",
        "label": "sextarius",
        "siLabel": "cubic metre"
    },
    "Q14623803": {
        "factor": "0.00000000000000000000166054",
        "unit": "Q11570",
        "label": "megadalton",
        "siLabel": "kilogram"
    },
    "Q14623804": {
        "factor": "0.000000000000000000000001660539067",
        "unit": "Q11570",
        "label": "kilodalton",
        "siLabel": "kilogram"
    },
    "Q14754979": {
        "factor": "1000000000000000000",
        "unit": "Q11570",
        "label": "zettagram",
        "siLabel": "kilogram"
    },
    "Q14786969": {
        "factor": "1000000",
        "unit": "Q25269",
        "label": "megajoule",
        "siLabel": "joule"
    },
    "Q14850704": {
        "factor": "1",
        "unit": "Q169893",
        "label": "mho",
        "siLabel": "siemens"
    },
    "Q14877141": {
        "factor": "26",
        "unit": "Q11570",
        "label": "Attic talent",
        "siLabel": "kilogram"
    },
    "Q14913554": {
        "factor": "1000000000000000000000000",
        "unit": "Q11574",
        "label": "yottasecond",
        "siLabel": "second"
    },
    "Q14916719": {
        "factor": "30856775814913700000000000",
        "unit": "Q11573",
        "label": "gigaparsec",
        "siLabel": "metre"
    },
    "Q14923662": {
        "factor": "1000000000000000000000000000000000000000000000",
        "unit": "Q25517",
        "label": "cubic petametre",
        "siLabel": "cubic metre"
    },
    "Q14948257": {
        "factor": "4184000000000000000",
        "unit": "Q25269",
        "label": "gigaton of TNT",
        "siLabel": "joule"
    },
    "Q15120301": {
        "factor": "101.325",
        "unit": "Q25269",
        "label": "litre atmosphere",
        "siLabel": "joule"
    },
    "Q15782509": {
        "factor": "0.004625",
        "unit": "Q25517",
        "label": "almuda",
        "siLabel": "cubic metre"
    },
    "Q15784325": {
        "factor": "0.0308568",
        "unit": "Q11573",
        "label": "attoparsec",
        "siLabel": "metre"
    },
    "Q15794456": {
        "factor": "0.001087",
        "unit": "Q25517",
        "label": "choinix",
        "siLabel": "cubic metre"
    },
    "Q15815815": {
        "factor": "0.0000481",
        "unit": "Q11570",
        "label": "Q15815815",
        "siLabel": "kilogram"
    },
    "Q15838121": {
        "factor": "0.077",
        "unit": "Q11573",
        "label": "palaiste",
        "siLabel": "metre"
    },
    "Q16511984": {
        "factor": "0.762",
        "unit": "Q11573",
        "label": "step",
        "siLabel": "metre"
    },
    "Q16683188": {
        "factor": "1",
        "unit": "Q16683188",
        "label": "watt per steradian",
        "siLabel": "watt per steradian"
    },
    "Q16831316": {
        "factor": "6.79",
        "unit": "Q11573",
        "label": "Q16831316",
        "siLabel": "metre"
    },
    "Q16859309": {
        "factor": "1.355818",
        "unit": "Q215571",
        "label": "pound-foot",
        "siLabel": "newton metre"
    },
    "Q16878358": {
        "factor": "0.836",
        "unit": "Q11573",
        "label": "vara",
        "siLabel": "metre"
    },
    "Q16928104": {
        "factor": "10000000000",
        "unit": "Q25343",
        "label": "Myriad",
        "siLabel": "square metre"
    },
    "Q17093295": {
        "factor": "0.000277778",
        "unit": "Q182429",
        "label": "metre per hour",
        "siLabel": "metre per second"
    },
    "Q17154097": {
        "factor": "6.283185307179586",
        "unit": "Q33680",
        "label": "perigon",
        "siLabel": "radian"
    },
    "Q17255465": {
        "factor": "0.000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004222",
        "unit": "Q25517",
        "label": "Planck volume",
        "siLabel": "cubic metre"
    },
    "Q17301921": {
        "factor": "2.796",
        "unit": "Q11573",
        "label": "destre",
        "siLabel": "metre"
    },
    "Q17301922": {
        "factor": "4986",
        "unit": "Q25343",
        "label": "cafissada",
        "siLabel": "square metre"
    },
    "Q18379097": {
        "factor": "0.0000000000000000000001",
        "unit": "Q95375885",
        "label": "solar flux unit",
        "siLabel": "watt per square metre hertz"
    },
    "Q18410485": {
        "factor": "0.052244",
        "unit": "Q11573",
        "label": "ava",
        "siLabel": "metre"
    },
    "Q18413919": {
        "factor": "0.01",
        "unit": "Q182429",
        "label": "centimetre per second",
        "siLabel": "metre per second"
    },
    "Q19285006": {
        "factor": "0.45719",
        "unit": "Q11573",
        "label": "hath",
        "siLabel": "metre"
    },
    "Q19392152": {
        "factor": "1000000000",
        "unit": "Q25517",
        "label": "teralitre",
        "siLabel": "cubic metre"
    },
    "Q19910723": {
        "factor": "1.778",
        "unit": "Q11573",
        "label": "makhovaya sazhen",
        "siLabel": "metre"
    },
    "Q20103787": {
        "factor": "0.01222",
        "unit": "Q25517",
        "label": "Q20103787",
        "siLabel": "cubic metre"
    },
    "Q20417984": {
        "factor": "44.44",
        "unit": "Q25343",
        "label": "Q20417984",
        "siLabel": "square metre"
    },
    "Q20423595": {
        "factor": "4444",
        "unit": "Q25343",
        "label": "Q20423595",
        "siLabel": "square metre"
    },
    "Q20706220": {
        "factor": "0.00001",
        "unit": "Q11573",
        "label": "centimillimetre",
        "siLabel": "metre"
    },
    "Q20706221": {
        "factor": "0.0001",
        "unit": "Q11573",
        "label": "decimillimetre",
        "siLabel": "metre"
    },
    "Q20850707": {
        "factor": "9.089",
        "unit": "Q25517",
        "label": "Q20850707",
        "siLabel": "cubic metre"
    },
    "Q20966435": {
        "factor": "1",
        "unit": "Q20966435",
        "label": "ampere per volt metre",
        "siLabel": "ampere per volt metre"
    },
    "Q20966455": {
        "factor": "1",
        "unit": "Q20966455",
        "label": "joule per mole kelvin",
        "siLabel": "joule per mole kelvin"
    },
    "Q21014455": {
        "factor": "0.0166666667",
        "unit": "Q182429",
        "label": "metre per minute",
        "siLabel": "metre per second"
    },
    "Q21016931": {
        "factor": "1",
        "unit": "Q21016931",
        "label": "pascal second",
        "siLabel": "pascal second"
    },
    "Q21061369": {
        "factor": "0.001",
        "unit": "Q199",
        "label": "gram per kilogram",
        "siLabel": "1"
    },
    "Q21062777": {
        "factor": "1000000",
        "unit": "Q44395",
        "label": "megapascal",
        "siLabel": "pascal"
    },
    "Q21064807": {
        "factor": "1000",
        "unit": "Q44395",
        "label": "kilopascal",
        "siLabel": "pascal"
    },
    "Q21064845": {
        "factor": "1000",
        "unit": "Q2415352",
        "label": "mole per litre",
        "siLabel": "mole per cubic metre"
    },
    "Q21074767": {
        "factor": "1138100",
        "unit": "Q25343",
        "label": "square verst",
        "siLabel": "square metre"
    },
    "Q21075844": {
        "factor": "0.001",
        "unit": "Q199",
        "label": "millilitre per litre",
        "siLabel": "1"
    },
    "Q21077820": {
        "factor": "0.000001",
        "unit": "Q844211",
        "label": "milligram per cubic metre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q21077849": {
        "factor": "1000",
        "unit": "Q57175225",
        "label": "kilojoule per kilogram",
        "siLabel": "joule per kilogram"
    },
    "Q21088638": {
        "factor": "1",
        "unit": "Q21088638",
        "label": "joule per tesla",
        "siLabel": "joule per tesla"
    },
    "Q21091747": {
        "factor": "0.000001",
        "unit": "Q199",
        "label": "milligram per kilogram",
        "siLabel": "1"
    },
    "Q21095810": {
        "factor": "1",
        "unit": "Q21095810",
        "label": "hertz per tesla",
        "siLabel": "hertz per tesla"
    },
    "Q21281991": {
        "factor": "1.019",
        "unit": "Q83216",
        "label": "international candle",
        "siLabel": "candela"
    },
    "Q21282164": {
        "factor": "1",
        "unit": "Q83216",
        "label": "new candle",
        "siLabel": "candela"
    },
    "Q21282180": {
        "factor": "0.903",
        "unit": "Q83216",
        "label": "Hefner candle",
        "siLabel": "candela"
    },
    "Q21294882": {
        "factor": "1",
        "unit": "Q21294882",
        "label": "farad per metre",
        "siLabel": "farad per metre"
    },
    "Q21344460": {
        "factor": "0.000000000001",
        "unit": "Q21294882",
        "label": "picofarad per metre",
        "siLabel": "farad per metre"
    },
    "Q21392882": {
        "factor": "1",
        "unit": "Q21392882",
        "label": "newton per square ampere",
        "siLabel": "newton per square ampere"
    },
    "Q21393312": {
        "factor": "1",
        "unit": "Q21393312",
        "label": "joule per kelvin",
        "siLabel": "joule per kelvin"
    },
    "Q21395031": {
        "factor": "1",
        "unit": "Q21395031",
        "label": "newton square metre per square kilogram",
        "siLabel": "newton square metre per square kilogram"
    },
    "Q21395834": {
        "factor": "1",
        "unit": "Q21395834",
        "label": "watt per square metre kelvin to the fourth power",
        "siLabel": "watt per square metre kelvin to the fourth power"
    },
    "Q21396202": {
        "factor": "1",
        "unit": "Q21396202",
        "label": "coulomb per mole",
        "siLabel": "coulomb per mole"
    },
    "Q21401573": {
        "factor": "1",
        "unit": "Q21401573",
        "label": "reciprocal cubic metre",
        "siLabel": "reciprocal cubic metre"
    },
    "Q21489891": {
        "factor": "0.000000000000000000000000001",
        "unit": "Q25517",
        "label": "cubic nanometre",
        "siLabel": "cubic metre"
    },
    "Q21489892": {
        "factor": "1000000000000000000000000000",
        "unit": "Q25517",
        "label": "cubic gigametre",
        "siLabel": "cubic metre"
    },
    "Q21489893": {
        "factor": "1000000000000000000",
        "unit": "Q25517",
        "label": "cubic megametre",
        "siLabel": "cubic metre"
    },
    "Q21489894": {
        "factor": "0.000000000000000001",
        "unit": "Q25517",
        "label": "cubic micrometre",
        "siLabel": "cubic metre"
    },
    "Q21500224": {
        "factor": "0.0000000048481368110954",
        "unit": "Q33680",
        "label": "milliarcsecond",
        "siLabel": "radian"
    },
    "Q21604951": {
        "factor": "0.001",
        "unit": "Q844211",
        "label": "gram per cubic metre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q21615967": {
        "factor": "1",
        "unit": "Q21615967",
        "label": "cubic metre per mole",
        "siLabel": "cubic metre per mole"
    },
    "Q21673990": {
        "factor": "0.00035277777777",
        "unit": "Q11573",
        "label": "DTP point",
        "siLabel": "metre"
    },
    "Q21719454": {
        "factor": "1",
        "unit": "Q21719454",
        "label": "metre per cubic second",
        "siLabel": "metre per cubic second"
    },
    "Q21866821": {
        "factor": "1948.8",
        "unit": "Q11573",
        "label": "great versta",
        "siLabel": "metre"
    },
    "Q22137107": {
        "factor": "0.0000000000000001536",
        "unit": "Q1063756",
        "label": "milliarcsecond per year",
        "siLabel": "radian per second"
    },
    "Q22350885": {
        "factor": "10",
        "unit": "Q25343",
        "label": "deciare",
        "siLabel": "square metre"
    },
    "Q22583210": {
        "factor": "0.777",
        "unit": "Q11573",
        "label": "Rif",
        "siLabel": "metre"
    },
    "Q22673229": {
        "factor": "0.00508",
        "unit": "Q182429",
        "label": "foot per minute",
        "siLabel": "metre per second"
    },
    "Q23210602": {
        "factor": "0.00000000000000000000000000000000000000000000001",
        "unit": "Q25269",
        "label": "biot",
        "siLabel": "joule"
    },
    "Q23808021": {
        "factor": "0.03110348",
        "unit": "Q11570",
        "label": "apothecaries' ounce",
        "siLabel": "kilogram"
    },
    "Q23823681": {
        "factor": "1000000000000",
        "unit": "Q25236",
        "label": "terawatt",
        "siLabel": "watt"
    },
    "Q23925410": {
        "factor": "0.004546099",
        "unit": "Q25517",
        "label": "gallon (UK)",
        "siLabel": "cubic metre"
    },
    "Q23925413": {
        "factor": "0.003785412",
        "unit": "Q25517",
        "label": "gallon (US)",
        "siLabel": "cubic metre"
    },
    "Q23925527": {
        "factor": "0.004621",
        "unit": "Q25517",
        "label": "beer gallon",
        "siLabel": "cubic metre"
    },
    "Q23931040": {
        "factor": "100",
        "unit": "Q25343",
        "label": "square decametre",
        "siLabel": "square metre"
    },
    "Q23931103": {
        "factor": "3434290.0120544",
        "unit": "Q25343",
        "label": "square nautical mile",
        "siLabel": "square metre"
    },
    "Q23931109": {
        "factor": "1000",
        "unit": "Q25343",
        "label": "metric dunam",
        "siLabel": "square metre"
    },
    "Q23931116": {
        "factor": "1300",
        "unit": "Q25343",
        "label": "Cypriot dunam",
        "siLabel": "square metre"
    },
    "Q23931127": {
        "factor": "2500",
        "unit": "Q25343",
        "label": "Iraqi dunam",
        "siLabel": "square metre"
    },
    "Q23931129": {
        "factor": "920",
        "unit": "Q25343",
        "label": "old dunam",
        "siLabel": "square metre"
    },
    "Q23931147": {
        "factor": "3.3",
        "unit": "Q25343",
        "label": "Q23931147",
        "siLabel": "square metre"
    },
    "Q23931245": {
        "factor": "3930",
        "unit": "Q25343",
        "label": "cuerda",
        "siLabel": "square metre"
    },
    "Q24008536": {
        "factor": "0.001",
        "unit": "Q21615967",
        "label": "cubic decimetre per mole",
        "siLabel": "cubic metre per mole"
    },
    "Q24008537": {
        "factor": "0.000001",
        "unit": "Q21615967",
        "label": "cubic centimetre per mole",
        "siLabel": "cubic metre per mole"
    },
    "Q24666811": {
        "factor": "1",
        "unit": "Q24666811",
        "label": "metre per farad",
        "siLabel": "metre per farad"
    },
    "Q25098783": {
        "factor": "0.00000000000111265",
        "unit": "Q169893",
        "label": "statmho",
        "siLabel": "siemens"
    },
    "Q25203121": {
        "factor": "109.728",
        "unit": "Q11573",
        "label": "skein",
        "siLabel": "metre"
    },
    "Q25212673": {
        "factor": "3.058219431936",
        "unit": "Q25517",
        "label": "stack",
        "siLabel": "cubic metre"
    },
    "Q25303759": {
        "factor": "898755178700",
        "unit": "Q47083",
        "label": "statohm",
        "siLabel": "ohm"
    },
    "Q25377184": {
        "factor": "1",
        "unit": "Q25377184",
        "label": "kilogram per square metre",
        "siLabel": "kilogram per square metre"
    },
    "Q25381181": {
        "factor": "1",
        "unit": "Q25381181",
        "label": "kilogram per second",
        "siLabel": "kilogram per second"
    },
    "Q25381678": {
        "factor": "1",
        "unit": "Q25381678",
        "label": "metre per second to the fourth power",
        "siLabel": "metre per second to the fourth power"
    },
    "Q25388071": {
        "factor": "795.3964",
        "unit": "Q25343",
        "label": "Sadon",
        "siLabel": "square metre"
    },
    "Q25448199": {
        "factor": "0.299792",
        "unit": "Q11573",
        "label": "light-nanosecond",
        "siLabel": "metre"
    },
    "Q25511288": {
        "factor": "0.0000000000000000000000000000001",
        "unit": "Q25343",
        "label": "millibarn",
        "siLabel": "square metre"
    },
    "Q25559952": {
        "factor": "0.000000000333564",
        "unit": "Q25272",
        "label": "statampere",
        "siLabel": "ampere"
    },
    "Q25835384": {
        "factor": "0.00432",
        "unit": "Q11570",
        "label": "Greek drachma",
        "siLabel": "kilogram"
    },
    "Q25840166": {
        "factor": "0.02691",
        "unit": "Q11570",
        "label": "Roman uncia",
        "siLabel": "kilogram"
    },
    "Q25906460": {
        "factor": "0.0193",
        "unit": "Q11573",
        "label": "dactylos",
        "siLabel": "metre"
    },
    "Q25907674": {
        "factor": "0.0185",
        "unit": "Q11573",
        "label": "digitus",
        "siLabel": "metre"
    },
    "Q25909370": {
        "factor": "185",
        "unit": "Q11573",
        "label": "stadium",
        "siLabel": "metre"
    },
    "Q25909383": {
        "factor": "950",
        "unit": "Q25343",
        "label": "square plethron",
        "siLabel": "square metre"
    },
    "Q25909387": {
        "factor": "0.095",
        "unit": "Q25343",
        "label": "Greek square foot",
        "siLabel": "square metre"
    },
    "Q25915415": {
        "factor": "1259",
        "unit": "Q25343",
        "label": "actus quadratus",
        "siLabel": "square metre"
    },
    "Q25915550": {
        "factor": "0.4436",
        "unit": "Q11573",
        "label": "pechys ephtymetrikos",
        "siLabel": "metre"
    },
    "Q25918986": {
        "factor": "370",
        "unit": "Q11573",
        "label": "diaulos",
        "siLabel": "metre"
    },
    "Q25919263": {
        "factor": "2220",
        "unit": "Q11573",
        "label": "dolichos",
        "siLabel": "metre"
    },
    "Q25927192": {
        "factor": "0.008696",
        "unit": "Q25517",
        "label": "hekteus",
        "siLabel": "cubic metre"
    },
    "Q25927234": {
        "factor": "0.00935",
        "unit": "Q25517",
        "label": "kophinos",
        "siLabel": "cubic metre"
    },
    "Q25932175": {
        "factor": "0.197",
        "unit": "Q25343",
        "label": "square cubit",
        "siLabel": "square metre"
    },
    "Q25999243": {
        "factor": "1",
        "unit": "Q25999243",
        "label": "kilogram per metre",
        "siLabel": "kilogram per metre"
    },
    "Q26156113": {
        "factor": "1",
        "unit": "Q26156113",
        "label": "newton per metre",
        "siLabel": "newton per metre"
    },
    "Q26156132": {
        "factor": "0.001",
        "unit": "Q26156113",
        "label": "millinewton per metre",
        "siLabel": "newton per metre"
    },
    "Q26158194": {
        "factor": "0.001",
        "unit": "Q21016931",
        "label": "millipascal second",
        "siLabel": "pascal second"
    },
    "Q26162530": {
        "factor": "0.000001",
        "unit": "Q3332099",
        "label": "centistokes",
        "siLabel": "square metre per second"
    },
    "Q26162545": {
        "factor": "0.0001",
        "unit": "Q3332099",
        "label": "square centimetre per second",
        "siLabel": "square metre per second"
    },
    "Q26162546": {
        "factor": "0.000001",
        "unit": "Q3332099",
        "label": "square millimetre per second",
        "siLabel": "square metre per second"
    },
    "Q26162557": {
        "factor": "0.001",
        "unit": "Q21016931",
        "label": "centipoise",
        "siLabel": "pascal second"
    },
    "Q26162587": {
        "factor": "0.000001",
        "unit": "Q21016931",
        "label": "micropascal second",
        "siLabel": "pascal second"
    },
    "Q26221041": {
        "factor": "4.55225",
        "unit": "Q25343",
        "label": "square sazhen",
        "siLabel": "square metre"
    },
    "Q26244070": {
        "factor": "503650",
        "unit": "Q25343",
        "label": "centuria",
        "siLabel": "square metre"
    },
    "Q26250779": {
        "factor": "0.5058",
        "unit": "Q25343",
        "label": "square arshin",
        "siLabel": "square metre"
    },
    "Q26267944": {
        "factor": "0.48513",
        "unit": "Q11573",
        "label": "Teon",
        "siLabel": "metre"
    },
    "Q26267949": {
        "factor": "225",
        "unit": "Q25343",
        "label": "Maunie",
        "siLabel": "square metre"
    },
    "Q26267953": {
        "factor": "0.00077",
        "unit": "Q25517",
        "label": "Anati",
        "siLabel": "cubic metre"
    },
    "Q26267960": {
        "factor": "0.001305",
        "unit": "Q25517",
        "label": "Selga",
        "siLabel": "cubic metre"
    },
    "Q26267965": {
        "factor": "66",
        "unit": "Q11573",
        "label": "Gamad",
        "siLabel": "metre"
    },
    "Q26267967": {
        "factor": "4883.2",
        "unit": "Q25343",
        "label": "Li\u00f1o",
        "siLabel": "square metre"
    },
    "Q26267974": {
        "factor": "0.13",
        "unit": "Q11573",
        "label": "Yuku",
        "siLabel": "metre"
    },
    "Q26267978": {
        "factor": "0.0001434",
        "unit": "Q25517",
        "label": "Gidda",
        "siLabel": "cubic metre"
    },
    "Q26267980": {
        "factor": "16187425.6896",
        "unit": "Q25343",
        "label": "Barony",
        "siLabel": "square metre"
    },
    "Q26268013": {
        "factor": "315",
        "unit": "Q25343",
        "label": "Clima",
        "siLabel": "square metre"
    },
    "Q26268015": {
        "factor": "0.000000707",
        "unit": "Q11570",
        "label": "khardal",
        "siLabel": "kilogram"
    },
    "Q26268018": {
        "factor": "1.917",
        "unit": "Q11573",
        "label": "Latro",
        "siLabel": "metre"
    },
    "Q26268024": {
        "factor": "3.3586",
        "unit": "Q25517",
        "label": "Last",
        "siLabel": "cubic metre"
    },
    "Q26268027": {
        "factor": "40000",
        "unit": "Q11570",
        "label": "Tenn",
        "siLabel": "kilogram"
    },
    "Q26268030": {
        "factor": "0.03634",
        "unit": "Q11573",
        "label": "Palaz",
        "siLabel": "metre"
    },
    "Q26268034": {
        "factor": "8515.72",
        "unit": "Q25343",
        "label": "Hond",
        "siLabel": "square metre"
    },
    "Q26268041": {
        "factor": "0.02577",
        "unit": "Q25517",
        "label": "Takar",
        "siLabel": "cubic metre"
    },
    "Q26268047": {
        "factor": "28390",
        "unit": "Q25343",
        "label": "Jonke",
        "siLabel": "square metre"
    },
    "Q26268049": {
        "factor": "0.003283",
        "unit": "Q25517",
        "label": "Chus",
        "siLabel": "cubic metre"
    },
    "Q26268051": {
        "factor": "0.0000459",
        "unit": "Q11570",
        "label": "Coccia",
        "siLabel": "kilogram"
    },
    "Q26268053": {
        "factor": "0.0002648",
        "unit": "Q25517",
        "label": "Chandoo",
        "siLabel": "cubic metre"
    },
    "Q26708069": {
        "factor": "4184",
        "unit": "Q25269",
        "label": "kilocalorie",
        "siLabel": "joule"
    },
    "Q26869687": {
        "factor": "0.000000462086",
        "unit": "Q25517",
        "label": "dash",
        "siLabel": "cubic metre"
    },
    "Q27057892": {
        "factor": "1.63293",
        "unit": "Q11570",
        "label": "viss",
        "siLabel": "kilogram"
    },
    "Q27188268": {
        "factor": "0.0166666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666666667",
        "unit": "Q794261",
        "label": "cubic metre per minute",
        "siLabel": "cubic metre per second"
    },
    "Q27861986": {
        "factor": "299792.458",
        "unit": "Q11573",
        "label": "light-millisecond",
        "siLabel": "metre"
    },
    "Q27863866": {
        "factor": "0.0000000010167",
        "unit": "Q11574",
        "label": "light-foot",
        "siLabel": "second"
    },
    "Q27864215": {
        "factor": "0.0036",
        "unit": "Q25269",
        "label": "microwatt-hour",
        "siLabel": "joule"
    },
    "Q27926203": {
        "factor": "229.8",
        "unit": "Q25343",
        "label": "Lekha",
        "siLabel": "square metre"
    },
    "Q27992625": {
        "factor": "3",
        "unit": "Q11570",
        "label": "men",
        "siLabel": "kilogram"
    },
    "Q28171715": {
        "factor": "1.8288",
        "unit": "Q11573",
        "label": "bow",
        "siLabel": "metre"
    },
    "Q28683485": {
        "factor": "1",
        "unit": "Q28683485",
        "label": "coulomb per kilogram",
        "siLabel": "coulomb per kilogram"
    },
    "Q28719934": {
        "factor": "0.00000000000000016022",
        "unit": "Q25269",
        "label": "kiloelectronvolt",
        "siLabel": "joule"
    },
    "Q28739766": {
        "factor": "1",
        "unit": "Q28739766",
        "label": "coulomb metre",
        "siLabel": "coulomb metre"
    },
    "Q28924752": {
        "factor": "0.001",
        "unit": "Q28924753",
        "label": "gram per mole",
        "siLabel": "kilogram per mole"
    },
    "Q28924753": {
        "factor": "1",
        "unit": "Q28924753",
        "label": "kilogram per mole",
        "siLabel": "kilogram per mole"
    },
    "Q29924639": {
        "factor": "1000",
        "unit": "Q550341",
        "label": "kilovolt ampere",
        "siLabel": "volt ampere"
    },
    "Q30001810": {
        "factor": "0.000000000000000001",
        "unit": "Q25272",
        "label": "attoampere",
        "siLabel": "ampere"
    },
    "Q30001811": {
        "factor": "0.000000000000000001",
        "unit": "Q102573",
        "label": "attobecquerel",
        "siLabel": "becquerel"
    },
    "Q30001812": {
        "factor": "0.000000000000000001",
        "unit": "Q83216",
        "label": "attocandela",
        "siLabel": "candela"
    },
    "Q30001813": {
        "factor": "0.000000000000000001",
        "unit": "Q25406",
        "label": "attocoulomb",
        "siLabel": "coulomb"
    },
    "Q30001814": {
        "factor": "0.000000000000000001",
        "unit": "Q39369",
        "label": "attohertz",
        "siLabel": "hertz"
    },
    "Q30001815": {
        "factor": "0.000000000000000001",
        "unit": "Q25269",
        "label": "attojoule",
        "siLabel": "joule"
    },
    "Q30001816": {
        "factor": "0.000000000000000001",
        "unit": "Q208634",
        "label": "attokatal",
        "siLabel": "katal"
    },
    "Q30001817": {
        "factor": "0.000000000000000001",
        "unit": "Q11579",
        "label": "attokelvin",
        "siLabel": "kelvin"
    },
    "Q30001819": {
        "factor": "0.000000000000000001",
        "unit": "Q484092",
        "label": "attolumen",
        "siLabel": "lumen"
    },
    "Q30001820": {
        "factor": "0.000000000000000001",
        "unit": "Q179836",
        "label": "attolux",
        "siLabel": "lux"
    },
    "Q30001821": {
        "factor": "0.000000000000000001",
        "unit": "Q41509",
        "label": "attomole",
        "siLabel": "mole"
    },
    "Q30001822": {
        "factor": "0.000000000000000001",
        "unit": "Q12438",
        "label": "attonewton",
        "siLabel": "newton"
    },
    "Q30001823": {
        "factor": "0.000000000000000001",
        "unit": "Q47083",
        "label": "attoohm",
        "siLabel": "ohm"
    },
    "Q30001825": {
        "factor": "0.000000000000000001",
        "unit": "Q44395",
        "label": "attopascal",
        "siLabel": "pascal"
    },
    "Q30001826": {
        "factor": "0.000000000000000001",
        "unit": "Q33680",
        "label": "attoradian",
        "siLabel": "radian"
    },
    "Q30001827": {
        "factor": "0.000000000000000001",
        "unit": "Q169893",
        "label": "attosiemens",
        "siLabel": "siemens"
    },
    "Q30001828": {
        "factor": "0.000000000000000001",
        "unit": "Q103246",
        "label": "attosievert",
        "siLabel": "sievert"
    },
    "Q30001829": {
        "factor": "0.000000000000000001",
        "unit": "Q177612",
        "label": "attosteradian",
        "siLabel": "steradian"
    },
    "Q30001830": {
        "factor": "0.000000000000000001",
        "unit": "Q163343",
        "label": "attotesla",
        "siLabel": "tesla"
    },
    "Q30001831": {
        "factor": "0.000000000000000001",
        "unit": "Q25250",
        "label": "attovolt",
        "siLabel": "volt"
    },
    "Q30001832": {
        "factor": "0.000000000000000001",
        "unit": "Q25236",
        "label": "attowatt",
        "siLabel": "watt"
    },
    "Q30001833": {
        "factor": "0.000000000000000001",
        "unit": "Q170804",
        "label": "attoweber",
        "siLabel": "weber"
    },
    "Q30063541": {
        "factor": "100000",
        "unit": "Q2844477",
        "label": "abampere per square centimetre",
        "siLabel": "ampere per square metre"
    },
    "Q30063612": {
        "factor": "100000",
        "unit": "Q68343206",
        "label": "abcoulomb per square centimetre",
        "siLabel": "coulomb per square metre"
    },
    "Q30063650": {
        "factor": "100000000000",
        "unit": "Q21294882",
        "label": "abfarad per centimetre",
        "siLabel": "farad per metre"
    },
    "Q30063714": {
        "factor": "1000000000",
        "unit": "Q169893",
        "label": "absiemens",
        "siLabel": "siemens"
    },
    "Q30063740": {
        "factor": "0.0001",
        "unit": "Q163343",
        "label": "abtesla",
        "siLabel": "tesla"
    },
    "Q30063903": {
        "factor": "0.0000000001",
        "unit": "Q83948162",
        "label": "abvolt centimetre",
        "siLabel": "volt metre"
    },
    "Q30063922": {
        "factor": "0.000001",
        "unit": "Q3562962",
        "label": "abvolt per centimetre",
        "siLabel": "volt per metre"
    },
    "Q30063933": {
        "factor": "0.00000001",
        "unit": "Q100293891",
        "label": "abvolt second",
        "siLabel": "volt second"
    },
    "Q30064054": {
        "factor": "57.2958",
        "unit": "Q30064202",
        "label": "ampere per degree",
        "siLabel": "ampere per radian"
    },
    "Q30064159": {
        "factor": "1",
        "unit": "Q30064159",
        "label": "ampere per joule",
        "siLabel": "ampere per joule"
    },
    "Q30064202": {
        "factor": "1",
        "unit": "Q30064202",
        "label": "ampere per radian",
        "siLabel": "ampere per radian"
    },
    "Q30066654": {
        "factor": "1550",
        "unit": "Q281096",
        "label": "candela per square inch",
        "siLabel": "candela per square metre"
    },
    "Q30080109": {
        "factor": "133200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
        "unit": "Q2844477",
        "label": "Planck current density",
        "siLabel": "ampere per square metre"
    },
    "Q30093584": {
        "factor": "3600",
        "unit": "Q25343",
        "label": "field",
        "siLabel": "square metre"
    },
    "Q30128253": {
        "factor": "0.0000425",
        "unit": "Q11570",
        "label": "korn",
        "siLabel": "kilogram"
    },
    "Q30338333": {
        "factor": "1",
        "unit": "Q30338333",
        "label": "radian per square second",
        "siLabel": "radian per square second"
    },
    "Q30338605": {
        "factor": "1",
        "unit": "Q30338605",
        "label": "radian per metre",
        "siLabel": "radian per metre"
    },
    "Q31197846": {
        "factor": "0.00032",
        "unit": "Q25517",
        "label": "log",
        "siLabel": "cubic metre"
    },
    "Q31842363": {
        "factor": "17400",
        "unit": "Q25343",
        "label": "quadra",
        "siLabel": "square metre"
    },
    "Q32304758": {
        "factor": "200",
        "unit": "Q11570",
        "label": "Rahar",
        "siLabel": "kilogram"
    },
    "Q32750621": {
        "factor": "0.0004731765",
        "unit": "Q25517",
        "label": "liquid pint (US)",
        "siLabel": "cubic metre"
    },
    "Q32750759": {
        "factor": "0.00002957353",
        "unit": "Q25517",
        "label": "fluid ounce (US)",
        "siLabel": "cubic metre"
    },
    "Q32750816": {
        "factor": "0.03523907",
        "unit": "Q25517",
        "label": "bushel (US)",
        "siLabel": "cubic metre"
    },
    "Q32751272": {
        "factor": "0.0005506105",
        "unit": "Q25517",
        "label": "dry pint (US)",
        "siLabel": "cubic metre"
    },
    "Q32751296": {
        "factor": "0.1156271",
        "unit": "Q25517",
        "label": "dry barrel (US)",
        "siLabel": "cubic metre"
    },
    "Q35152984": {
        "factor": "0.07989",
        "unit": "Q25517",
        "label": "Wecht",
        "siLabel": "cubic metre"
    },
    "Q39359957": {
        "factor": "1853.181",
        "unit": "Q11573",
        "label": "UK nautical miles",
        "siLabel": "metre"
    },
    "Q39360235": {
        "factor": "4828.042",
        "unit": "Q11573",
        "label": "US leagues",
        "siLabel": "metre"
    },
    "Q39360471": {
        "factor": "5556",
        "unit": "Q11573",
        "label": "nautical leagues",
        "siLabel": "metre"
    },
    "Q39362962": {
        "factor": "0.0000000254",
        "unit": "Q11573",
        "label": "microinch",
        "siLabel": "metre"
    },
    "Q39363132": {
        "factor": "4828",
        "unit": "Q11573",
        "label": "UK leagues",
        "siLabel": "metre"
    },
    "Q39363209": {
        "factor": "5559.552",
        "unit": "Q11573",
        "label": "UK nautical leagues",
        "siLabel": "metre"
    },
    "Q39380159": {
        "factor": "1853.24",
        "unit": "Q11573",
        "label": "US nautical miles",
        "siLabel": "metre"
    },
    "Q39462789": {
        "factor": "0.0000000000000006451484",
        "unit": "Q25343",
        "label": "square microinch",
        "siLabel": "square metre"
    },
    "Q39467934": {
        "factor": "9.80665",
        "unit": "Q44395",
        "label": "kilogram-force per square metre",
        "siLabel": "pascal"
    },
    "Q39469927": {
        "factor": "1",
        "unit": "Q39469927",
        "label": "newton per square metre",
        "siLabel": "newton per square metre"
    },
    "Q39617688": {
        "factor": "50.80235",
        "unit": "Q11570",
        "label": "long hundredweight",
        "siLabel": "kilogram"
    },
    "Q39617818": {
        "factor": "0.3732417",
        "unit": "Q11570",
        "label": "troy pound",
        "siLabel": "kilogram"
    },
    "Q39628023": {
        "factor": "31556952",
        "unit": "Q11574",
        "label": "Gregorian year",
        "siLabel": "second"
    },
    "Q39699418": {
        "factor": "0.01",
        "unit": "Q1051665",
        "label": "centimetre per square second",
        "siLabel": "metre per square second"
    },
    "Q39706616": {
        "factor": "185.2",
        "unit": "Q11573",
        "label": "cable length (International)",
        "siLabel": "metre"
    },
    "Q39706694": {
        "factor": "219.456",
        "unit": "Q11573",
        "label": "cable length (US)",
        "siLabel": "metre"
    },
    "Q39708248": {
        "factor": "1000000000000",
        "unit": "Q11573",
        "label": "spat",
        "siLabel": "metre"
    },
    "Q39708821": {
        "factor": "0.2286",
        "unit": "Q11573",
        "label": "quater",
        "siLabel": "metre"
    },
    "Q39709980": {
        "factor": "0.00774192",
        "unit": "Q25343",
        "label": "board",
        "siLabel": "square metre"
    },
    "Q39710113": {
        "factor": "12.958174",
        "unit": "Q25343",
        "label": "boiler horsepower equivalent direct radiation",
        "siLabel": "square metre"
    },
    "Q39710583": {
        "factor": "1.48644864",
        "unit": "Q25343",
        "label": "cord",
        "siLabel": "square metre"
    },
    "Q39978339": {
        "factor": "10000",
        "unit": "Q25377184",
        "label": "kilogram per square centimetre",
        "siLabel": "kilogram per square metre"
    },
    "Q39998555": {
        "factor": "0.01745329251994329576923690768488612713",
        "unit": "Q1063756",
        "label": "degree per second",
        "siLabel": "radian per second"
    },
    "Q41588368": {
        "factor": "1",
        "unit": "Q41588368",
        "label": "metre kelvin",
        "siLabel": "metre kelvin"
    },
    "Q47491611": {
        "factor": "0.01905",
        "unit": "Q11573",
        "label": "Angulli",
        "siLabel": "metre"
    },
    "Q50190518": {
        "factor": "4.88242764",
        "unit": "Q25377184",
        "label": "pounds per square foot",
        "siLabel": "kilogram per square metre"
    },
    "Q50808017": {
        "factor": "1",
        "unit": "Q50808017",
        "label": "kilogram square metre",
        "siLabel": "kilogram square metre"
    },
    "Q51885434": {
        "factor": "0.074",
        "unit": "Q11573",
        "label": "palmus",
        "siLabel": "metre"
    },
    "Q53223136": {
        "factor": "1.2096",
        "unit": "Q11574",
        "label": "microfortnight",
        "siLabel": "second"
    },
    "Q53393488": {
        "factor": "1000000000000000",
        "unit": "Q39369",
        "label": "petahertz",
        "siLabel": "hertz"
    },
    "Q53393490": {
        "factor": "1000000000000000000",
        "unit": "Q39369",
        "label": "exahertz",
        "siLabel": "hertz"
    },
    "Q53393494": {
        "factor": "1000000000000000000000",
        "unit": "Q39369",
        "label": "zettahertz",
        "siLabel": "hertz"
    },
    "Q53393498": {
        "factor": "1000000000000000000000000",
        "unit": "Q39369",
        "label": "yottahertz",
        "siLabel": "hertz"
    },
    "Q53393659": {
        "factor": "1000",
        "unit": "Q25517",
        "label": "megalitre",
        "siLabel": "cubic metre"
    },
    "Q53393664": {
        "factor": "1000000",
        "unit": "Q25517",
        "label": "gigalitre",
        "siLabel": "cubic metre"
    },
    "Q53393669": {
        "factor": "1000000000000000",
        "unit": "Q25517",
        "label": "exalitre",
        "siLabel": "cubic metre"
    },
    "Q53393674": {
        "factor": "1000000000000000000",
        "unit": "Q25517",
        "label": "zettalitre",
        "siLabel": "cubic metre"
    },
    "Q53393678": {
        "factor": "1000000000000000000000",
        "unit": "Q25517",
        "label": "yottalitre",
        "siLabel": "cubic metre"
    },
    "Q53393768": {
        "factor": "0.000000000000000000000001",
        "unit": "Q25517",
        "label": "zeptolitre",
        "siLabel": "cubic metre"
    },
    "Q53393771": {
        "factor": "0.000000000000000000000000001",
        "unit": "Q25517",
        "label": "yoctolitre",
        "siLabel": "cubic metre"
    },
    "Q53393868": {
        "factor": "1000000000",
        "unit": "Q25269",
        "label": "gigajoule",
        "siLabel": "joule"
    },
    "Q53393886": {
        "factor": "1000000000000000",
        "unit": "Q25269",
        "label": "petajoule",
        "siLabel": "joule"
    },
    "Q53393890": {
        "factor": "1000000000000000000",
        "unit": "Q25269",
        "label": "exajoule",
        "siLabel": "joule"
    },
    "Q53393893": {
        "factor": "1000000000000000000000",
        "unit": "Q25269",
        "label": "zettajoule",
        "siLabel": "joule"
    },
    "Q53393898": {
        "factor": "1000000000000000000000000",
        "unit": "Q25269",
        "label": "yottajoule",
        "siLabel": "joule"
    },
    "Q53448786": {
        "factor": "0.000000000000000000000001",
        "unit": "Q39369",
        "label": "yoctohertz",
        "siLabel": "hertz"
    },
    "Q53448790": {
        "factor": "0.000000000000000000001",
        "unit": "Q39369",
        "label": "zeptohertz",
        "siLabel": "hertz"
    },
    "Q53448794": {
        "factor": "0.000000000000001",
        "unit": "Q39369",
        "label": "femtohertz",
        "siLabel": "hertz"
    },
    "Q53448797": {
        "factor": "0.000000000001",
        "unit": "Q39369",
        "label": "picohertz",
        "siLabel": "hertz"
    },
    "Q53448801": {
        "factor": "0.000000001",
        "unit": "Q39369",
        "label": "nanohertz",
        "siLabel": "hertz"
    },
    "Q53448806": {
        "factor": "0.000001",
        "unit": "Q39369",
        "label": "microhertz",
        "siLabel": "hertz"
    },
    "Q53448808": {
        "factor": "0.001",
        "unit": "Q39369",
        "label": "millihertz",
        "siLabel": "hertz"
    },
    "Q53448813": {
        "factor": "0.01",
        "unit": "Q39369",
        "label": "centihertz",
        "siLabel": "hertz"
    },
    "Q53448817": {
        "factor": "0.1",
        "unit": "Q39369",
        "label": "decihertz",
        "siLabel": "hertz"
    },
    "Q53448820": {
        "factor": "10",
        "unit": "Q39369",
        "label": "decahertz",
        "siLabel": "hertz"
    },
    "Q53448826": {
        "factor": "100",
        "unit": "Q39369",
        "label": "hectohertz",
        "siLabel": "hertz"
    },
    "Q53448828": {
        "factor": "0.000000000000000000000001",
        "unit": "Q25269",
        "label": "yoctojoule",
        "siLabel": "joule"
    },
    "Q53448832": {
        "factor": "0.000000000000000000001",
        "unit": "Q25269",
        "label": "zeptojoule",
        "siLabel": "joule"
    },
    "Q53448835": {
        "factor": "0.000000000000001",
        "unit": "Q25269",
        "label": "femtojoule",
        "siLabel": "joule"
    },
    "Q53448842": {
        "factor": "0.000000000001",
        "unit": "Q25269",
        "label": "picojoule",
        "siLabel": "joule"
    },
    "Q53448844": {
        "factor": "0.000000001",
        "unit": "Q25269",
        "label": "nanojoule",
        "siLabel": "joule"
    },
    "Q53448847": {
        "factor": "0.000001",
        "unit": "Q25269",
        "label": "microjoule",
        "siLabel": "joule"
    },
    "Q53448851": {
        "factor": "0.001",
        "unit": "Q25269",
        "label": "millijoule",
        "siLabel": "joule"
    },
    "Q53448856": {
        "factor": "0.01",
        "unit": "Q25269",
        "label": "centijoule",
        "siLabel": "joule"
    },
    "Q53448860": {
        "factor": "0.1",
        "unit": "Q25269",
        "label": "decijoule",
        "siLabel": "joule"
    },
    "Q53448864": {
        "factor": "10",
        "unit": "Q25269",
        "label": "decajoule",
        "siLabel": "joule"
    },
    "Q53448875": {
        "factor": "100",
        "unit": "Q25269",
        "label": "hectojoule",
        "siLabel": "joule"
    },
    "Q53448879": {
        "factor": "0.000000000000000000000001",
        "unit": "Q44395",
        "label": "yoctopascal",
        "siLabel": "pascal"
    },
    "Q53448883": {
        "factor": "0.000000000000000000001",
        "unit": "Q44395",
        "label": "zeptopascal",
        "siLabel": "pascal"
    },
    "Q53448886": {
        "factor": "0.000000000000001",
        "unit": "Q44395",
        "label": "femtopascal",
        "siLabel": "pascal"
    },
    "Q53448892": {
        "factor": "0.000000000001",
        "unit": "Q44395",
        "label": "picopascal",
        "siLabel": "pascal"
    },
    "Q53448897": {
        "factor": "0.000000001",
        "unit": "Q44395",
        "label": "nanopascal",
        "siLabel": "pascal"
    },
    "Q53448900": {
        "factor": "0.000001",
        "unit": "Q44395",
        "label": "micropascal",
        "siLabel": "pascal"
    },
    "Q53448906": {
        "factor": "0.001",
        "unit": "Q44395",
        "label": "millipascal",
        "siLabel": "pascal"
    },
    "Q53448909": {
        "factor": "0.01",
        "unit": "Q44395",
        "label": "centipascal",
        "siLabel": "pascal"
    },
    "Q53448914": {
        "factor": "0.1",
        "unit": "Q44395",
        "label": "decipascal",
        "siLabel": "pascal"
    },
    "Q53448918": {
        "factor": "10",
        "unit": "Q44395",
        "label": "decapascal",
        "siLabel": "pascal"
    },
    "Q53448922": {
        "factor": "1000000000",
        "unit": "Q44395",
        "label": "gigapascal",
        "siLabel": "pascal"
    },
    "Q53448927": {
        "factor": "1000000000000",
        "unit": "Q44395",
        "label": "terapascal",
        "siLabel": "pascal"
    },
    "Q53448931": {
        "factor": "1000000000000000",
        "unit": "Q44395",
        "label": "petapascal",
        "siLabel": "pascal"
    },
    "Q53448936": {
        "factor": "1000000000000000000",
        "unit": "Q44395",
        "label": "exapascal",
        "siLabel": "pascal"
    },
    "Q53448939": {
        "factor": "1000000000000000000000",
        "unit": "Q44395",
        "label": "zettapascal",
        "siLabel": "pascal"
    },
    "Q53448943": {
        "factor": "1000000000000000000000000",
        "unit": "Q44395",
        "label": "yottapascal",
        "siLabel": "pascal"
    },
    "Q53448949": {
        "factor": "0.000000000000000000000001",
        "unit": "Q25250",
        "label": "yoctovolt",
        "siLabel": "volt"
    },
    "Q53448952": {
        "factor": "0.000000000000000000001",
        "unit": "Q25250",
        "label": "zeptovolt",
        "siLabel": "volt"
    },
    "Q53448957": {
        "factor": "0.000000000000001",
        "unit": "Q25250",
        "label": "femtovolt",
        "siLabel": "volt"
    },
    "Q53448960": {
        "factor": "0.000000000001",
        "unit": "Q25250",
        "label": "picovolt",
        "siLabel": "volt"
    },
    "Q53448965": {
        "factor": "0.000000001",
        "unit": "Q25250",
        "label": "nanovolt",
        "siLabel": "volt"
    },
    "Q53448969": {
        "factor": "0.01",
        "unit": "Q25250",
        "label": "centivolt",
        "siLabel": "volt"
    },
    "Q53448973": {
        "factor": "0.1",
        "unit": "Q25250",
        "label": "decivolt",
        "siLabel": "volt"
    },
    "Q53448977": {
        "factor": "10",
        "unit": "Q25250",
        "label": "decavolt",
        "siLabel": "volt"
    },
    "Q53448981": {
        "factor": "100",
        "unit": "Q25250",
        "label": "hectovolt",
        "siLabel": "volt"
    },
    "Q53448985": {
        "factor": "1000000000000",
        "unit": "Q25250",
        "label": "teravolt",
        "siLabel": "volt"
    },
    "Q53448990": {
        "factor": "1000000000000000",
        "unit": "Q25250",
        "label": "petavolt",
        "siLabel": "volt"
    },
    "Q53448994": {
        "factor": "1000000000000000000",
        "unit": "Q25250",
        "label": "exavolt",
        "siLabel": "volt"
    },
    "Q53448996": {
        "factor": "1000000000000000000000",
        "unit": "Q25250",
        "label": "zettavolt",
        "siLabel": "volt"
    },
    "Q53449001": {
        "factor": "1000000000000000000000000",
        "unit": "Q25250",
        "label": "yottavolt",
        "siLabel": "volt"
    },
    "Q53449006": {
        "factor": "0.000000000000000000000001",
        "unit": "Q25236",
        "label": "yoctowatt",
        "siLabel": "watt"
    },
    "Q53449008": {
        "factor": "0.000000000000000000001",
        "unit": "Q25236",
        "label": "zeptowatt",
        "siLabel": "watt"
    },
    "Q53449013": {
        "factor": "0.000000000000001",
        "unit": "Q25236",
        "label": "femtowatt",
        "siLabel": "watt"
    },
    "Q53449018": {
        "factor": "0.000000000001",
        "unit": "Q25236",
        "label": "picowatt",
        "siLabel": "watt"
    },
    "Q53449021": {
        "factor": "0.000000001",
        "unit": "Q25236",
        "label": "nanowatt",
        "siLabel": "watt"
    },
    "Q53449025": {
        "factor": "0.01",
        "unit": "Q25236",
        "label": "centiwatt",
        "siLabel": "watt"
    },
    "Q53449029": {
        "factor": "0.1",
        "unit": "Q25236",
        "label": "deciwatt",
        "siLabel": "watt"
    },
    "Q53449033": {
        "factor": "10",
        "unit": "Q25236",
        "label": "decawatt",
        "siLabel": "watt"
    },
    "Q53449036": {
        "factor": "100",
        "unit": "Q25236",
        "label": "hectowatt",
        "siLabel": "watt"
    },
    "Q53449040": {
        "factor": "1000000000000000",
        "unit": "Q25236",
        "label": "petawatt",
        "siLabel": "watt"
    },
    "Q53449045": {
        "factor": "1000000000000000000",
        "unit": "Q25236",
        "label": "exawatt",
        "siLabel": "watt"
    },
    "Q53449049": {
        "factor": "1000000000000000000000",
        "unit": "Q25236",
        "label": "zettawatt",
        "siLabel": "watt"
    },
    "Q53449054": {
        "factor": "1000000000000000000000000",
        "unit": "Q25236",
        "label": "yottawatt",
        "siLabel": "watt"
    },
    "Q53651160": {
        "factor": "0.000000000000000000000000000000000000000000000000000000000000001",
        "unit": "Q25517",
        "label": "cubic zeptometre",
        "siLabel": "cubic metre"
    },
    "Q53651201": {
        "factor": "1000000000000000000000000000000000000000000000000000000000000000000000000",
        "unit": "Q25517",
        "label": "cubic yottametre",
        "siLabel": "cubic metre"
    },
    "Q53651356": {
        "factor": "0.000000000000000000000000000000000000000000000000000000000000000000000001",
        "unit": "Q25517",
        "label": "cubic yoctometre",
        "siLabel": "cubic metre"
    },
    "Q53651512": {
        "factor": "0.000000000000000000000000000000000001",
        "unit": "Q25517",
        "label": "cubic picometre",
        "siLabel": "cubic metre"
    },
    "Q53651713": {
        "factor": "0.000000000000000000000000000000000000000000001",
        "unit": "Q25517",
        "label": "cubic femtometre",
        "siLabel": "cubic metre"
    },
    "Q53679433": {
        "factor": "1000",
        "unit": "Q25272",
        "label": "kiloampere",
        "siLabel": "ampere"
    },
    "Q53679437": {
        "factor": "0.000000000000001",
        "unit": "Q25272",
        "label": "femtoampere",
        "siLabel": "ampere"
    },
    "Q53679438": {
        "factor": "100",
        "unit": "Q25272",
        "label": "hectoampere",
        "siLabel": "ampere"
    },
    "Q53679439": {
        "factor": "0.1",
        "unit": "Q25272",
        "label": "deciampere",
        "siLabel": "ampere"
    },
    "Q53679440": {
        "factor": "10",
        "unit": "Q25272",
        "label": "decaampere",
        "siLabel": "ampere"
    },
    "Q53679441": {
        "factor": "1000000000000000000",
        "unit": "Q25272",
        "label": "exaampere",
        "siLabel": "ampere"
    },
    "Q53679443": {
        "factor": "1000000",
        "unit": "Q25272",
        "label": "megaampere",
        "siLabel": "ampere"
    },
    "Q53679444": {
        "factor": "1000000000000000",
        "unit": "Q25272",
        "label": "petaampere",
        "siLabel": "ampere"
    },
    "Q53679445": {
        "factor": "0.000000000000000000001",
        "unit": "Q25272",
        "label": "zeptoampere",
        "siLabel": "ampere"
    },
    "Q53679446": {
        "factor": "1000000000000000000000",
        "unit": "Q25272",
        "label": "zettaampere",
        "siLabel": "ampere"
    },
    "Q53679447": {
        "factor": "1000000000000000000000000",
        "unit": "Q25272",
        "label": "yottaampere",
        "siLabel": "ampere"
    },
    "Q53679449": {
        "factor": "0.000000000000000000000001",
        "unit": "Q25272",
        "label": "yoctoampere",
        "siLabel": "ampere"
    },
    "Q53679476": {
        "factor": "0.01",
        "unit": "Q25272",
        "label": "centiampere",
        "siLabel": "ampere"
    },
    "Q53679480": {
        "factor": "1000000000",
        "unit": "Q25272",
        "label": "gigaampere",
        "siLabel": "ampere"
    },
    "Q53679486": {
        "factor": "0.000000001",
        "unit": "Q25272",
        "label": "nanoampere",
        "siLabel": "ampere"
    },
    "Q53679489": {
        "factor": "0.000000000001",
        "unit": "Q25272",
        "label": "picoampere",
        "siLabel": "ampere"
    },
    "Q53679495": {
        "factor": "1000000000000",
        "unit": "Q25272",
        "label": "teraampere",
        "siLabel": "ampere"
    },
    "Q53951982": {
        "factor": "1000000000",
        "unit": "Q11570",
        "label": "megatonne",
        "siLabel": "kilogram"
    },
    "Q53952048": {
        "factor": "1000000",
        "unit": "Q11570",
        "label": "kilotonne",
        "siLabel": "kilogram"
    },
    "Q54006645": {
        "factor": "1000000000000000000000",
        "unit": "Q170804",
        "label": "zettaweber",
        "siLabel": "weber"
    },
    "Q54081354": {
        "factor": "1000000000000000000000",
        "unit": "Q163343",
        "label": "zettatesla",
        "siLabel": "tesla"
    },
    "Q54081925": {
        "factor": "1000000000000000000000",
        "unit": "Q103246",
        "label": "zettasievert",
        "siLabel": "sievert"
    },
    "Q54082468": {
        "factor": "1000000000000000000000",
        "unit": "Q169893",
        "label": "zettasiemens",
        "siLabel": "siemens"
    },
    "Q54083144": {
        "factor": "1000000000000000000000",
        "unit": "Q47083",
        "label": "zettaohm",
        "siLabel": "ohm"
    },
    "Q54083318": {
        "factor": "1000000000000000000000",
        "unit": "Q12438",
        "label": "zettanewton",
        "siLabel": "newton"
    },
    "Q54083566": {
        "factor": "1000000000000000000000",
        "unit": "Q484092",
        "label": "zettalumen",
        "siLabel": "lumen"
    },
    "Q54083579": {
        "factor": "1000000000000000000000",
        "unit": "Q179836",
        "label": "zettalux",
        "siLabel": "lux"
    },
    "Q54083593": {
        "factor": "1000000000000000000000",
        "unit": "Q41509",
        "label": "zettamole",
        "siLabel": "mole"
    },
    "Q54083712": {
        "factor": "1000000000000000000000",
        "unit": "Q102573",
        "label": "zettabecquerel",
        "siLabel": "becquerel"
    },
    "Q54083726": {
        "factor": "1000000000000000000000",
        "unit": "Q83216",
        "label": "zettacandela",
        "siLabel": "candela"
    },
    "Q54083746": {
        "factor": "1000000000000000000000",
        "unit": "Q25406",
        "label": "zettacoulomb",
        "siLabel": "coulomb"
    },
    "Q54083766": {
        "factor": "1000000000000000000000",
        "unit": "Q131255",
        "label": "zettafarad",
        "siLabel": "farad"
    },
    "Q54083779": {
        "factor": "1000000000000000000000",
        "unit": "Q190095",
        "label": "zettagray",
        "siLabel": "gray"
    },
    "Q54083795": {
        "factor": "1000000000000000000000",
        "unit": "Q163354",
        "label": "zettahenry",
        "siLabel": "henry"
    },
    "Q54083813": {
        "factor": "1000000000000000000000",
        "unit": "Q208634",
        "label": "zettakatal",
        "siLabel": "katal"
    },
    "Q54083824": {
        "factor": "1000000000000000000000",
        "unit": "Q11579",
        "label": "zettakelvin",
        "siLabel": "kelvin"
    },
    "Q55221232": {
        "factor": "0.6",
        "unit": "Q11570",
        "label": "geun",
        "siLabel": "kilogram"
    },
    "Q55433914": {
        "factor": "10",
        "unit": "Q844211",
        "label": "gram per decilitre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q55435156": {
        "factor": "0.01",
        "unit": "Q844211",
        "label": "milligram per decilitre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q55435387": {
        "factor": "1",
        "unit": "Q2415352",
        "label": "millimole per litre",
        "siLabel": "mole per cubic metre"
    },
    "Q55443011": {
        "factor": "0.00001",
        "unit": "Q844211",
        "label": "microgram per decilitre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q55726194": {
        "factor": "0.001",
        "unit": "Q844211",
        "label": "milligram per litre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q55737756": {
        "factor": "3",
        "unit": "Q11573",
        "label": "jang",
        "siLabel": "metre"
    },
    "Q55847187": {
        "factor": "0.008",
        "unit": "Q11570",
        "label": "Q55847187",
        "siLabel": "kilogram"
    },
    "Q56023789": {
        "factor": "1",
        "unit": "Q56023789",
        "label": "joule per metre",
        "siLabel": "joule per metre"
    },
    "Q56156859": {
        "factor": "0.001",
        "unit": "Q41509",
        "label": "millimole",
        "siLabel": "mole"
    },
    "Q56156949": {
        "factor": "0.000001",
        "unit": "Q41509",
        "label": "micromole",
        "siLabel": "mole"
    },
    "Q56157046": {
        "factor": "0.000000001",
        "unit": "Q41509",
        "label": "nanomole",
        "siLabel": "mole"
    },
    "Q56157048": {
        "factor": "0.000000000001",
        "unit": "Q41509",
        "label": "picomole",
        "siLabel": "mole"
    },
    "Q56160006": {
        "factor": "0.00000001",
        "unit": "Q844211",
        "label": "nanogram per decilitre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q56160020": {
        "factor": "0.00000000001",
        "unit": "Q844211",
        "label": "picogram per decilitre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q56160603": {
        "factor": "0.000000000000001",
        "unit": "Q41509",
        "label": "femtomole",
        "siLabel": "mole"
    },
    "Q56294502": {
        "factor": "1358.37",
        "unit": "Q11573",
        "label": "Kosa",
        "siLabel": "metre"
    },
    "Q56317116": {
        "factor": "0.00001",
        "unit": "Q1051665",
        "label": "milligal",
        "siLabel": "metre per square second"
    },
    "Q56317622": {
        "factor": "0.0000000000000000000000000000000000000000000000000000000000000783",
        "unit": "Q794261",
        "label": "Planck flow rate",
        "siLabel": "cubic metre per second"
    },
    "Q56318907": {
        "factor": "100000000",
        "unit": "Q44395",
        "label": "kilobar",
        "siLabel": "pascal"
    },
    "Q56402798": {
        "factor": "1000",
        "unit": "Q12438",
        "label": "kilonewton",
        "siLabel": "newton"
    },
    "Q57052317": {
        "factor": "1000",
        "unit": "Q80374519",
        "label": "kilojoule per square metre",
        "siLabel": "joule per square metre"
    },
    "Q57175165": {
        "factor": "1000000",
        "unit": "Q57175225",
        "label": "megajoule per kilogram",
        "siLabel": "joule per kilogram"
    },
    "Q57175225": {
        "factor": "1",
        "unit": "Q57175225",
        "label": "joule per kilogram",
        "siLabel": "joule per kilogram"
    },
    "Q57175557": {
        "factor": "0.001",
        "unit": "Q3332095",
        "label": "litre per kilogram",
        "siLabel": "cubic metre per kilogram"
    },
    "Q57273614": {
        "factor": "0.0000166667",
        "unit": "Q182429",
        "label": "millimetre per minute",
        "siLabel": "metre per second"
    },
    "Q57306331": {
        "factor": "0.1",
        "unit": "Q86200529",
        "label": "square centimetre per gram",
        "siLabel": "square metre per kilogram"
    },
    "Q57899268": {
        "factor": "0.001",
        "unit": "Q3332095",
        "label": "cubic metre per ton",
        "siLabel": "cubic metre per kilogram"
    },
    "Q58876528": {
        "factor": "0.0316887646",
        "unit": "Q794261",
        "label": "cubic hectometre per year",
        "siLabel": "cubic metre per second"
    },
    "Q59934067": {
        "factor": "10",
        "unit": "Q844211",
        "label": "gram per 100 millilitres",
        "siLabel": "kilogram per cubic metre"
    },
    "Q60742631": {
        "factor": "4743.717361111111",
        "unit": "Q182429",
        "label": "astronomical unit per year",
        "siLabel": "metre per second"
    },
    "Q60846970": {
        "factor": "0.000722",
        "unit": "Q25517",
        "label": "michetta",
        "siLabel": "cubic metre"
    },
    "Q60981881": {
        "factor": "0.00761",
        "unit": "Q11570",
        "label": "pim",
        "siLabel": "kilogram"
    },
    "Q61749562": {
        "factor": "1609.347",
        "unit": "Q11573",
        "label": "mile (US survey)",
        "siLabel": "metre"
    },
    "Q61749573": {
        "factor": "0.3048006",
        "unit": "Q11573",
        "label": "foot (US survey)",
        "siLabel": "metre"
    },
    "Q61750260": {
        "factor": "1609.344",
        "unit": "Q11573",
        "label": "international mile",
        "siLabel": "metre"
    },
    "Q61756607": {
        "factor": "0.9144",
        "unit": "Q11573",
        "label": "international yard",
        "siLabel": "metre"
    },
    "Q61769985": {
        "factor": "0.914402",
        "unit": "Q11573",
        "label": "US survey yards",
        "siLabel": "metre"
    },
    "Q61771602": {
        "factor": "0.3048",
        "unit": "Q11573",
        "label": "international foot",
        "siLabel": "metre"
    },
    "Q61771670": {
        "factor": "0.0254",
        "unit": "Q11573",
        "label": "international inch",
        "siLabel": "metre"
    },
    "Q61792336": {
        "factor": "0.2011684",
        "unit": "Q11573",
        "label": "United States survey link",
        "siLabel": "metre"
    },
    "Q61793198": {
        "factor": "5.02921",
        "unit": "Q11573",
        "label": "rod (US survey)",
        "siLabel": "metre"
    },
    "Q61793679": {
        "factor": "20.1168",
        "unit": "Q11573",
        "label": "international chain",
        "siLabel": "metre"
    },
    "Q61794388": {
        "factor": "1.8288",
        "unit": "Q11573",
        "label": "international fathom",
        "siLabel": "metre"
    },
    "Q61794766": {
        "factor": "20.11684",
        "unit": "Q11573",
        "label": "Gunter's chain (US survey)",
        "siLabel": "metre"
    },
    "Q61794946": {
        "factor": "201.168",
        "unit": "Q11573",
        "label": "international furlong",
        "siLabel": "metre"
    },
    "Q61992237": {
        "factor": "0.0000000115741",
        "unit": "Q794261",
        "label": "litre per day",
        "siLabel": "cubic metre per second"
    },
    "Q61992243": {
        "factor": "0.00000000038",
        "unit": "Q794261",
        "label": "litre per month",
        "siLabel": "cubic metre per second"
    },
    "Q61992246": {
        "factor": "0.0000000000317098",
        "unit": "Q794261",
        "label": "litre per year",
        "siLabel": "cubic metre per second"
    },
    "Q61996348": {
        "factor": "0.001",
        "unit": "Q794261",
        "label": "litre per second",
        "siLabel": "cubic metre per second"
    },
    "Q64448128": {
        "factor": "0.000011574074",
        "unit": "Q794261",
        "label": "cubic metre per day",
        "siLabel": "cubic metre per second"
    },
    "Q64748817": {
        "factor": "3600",
        "unit": "Q80374519",
        "label": "watt hour per square metre",
        "siLabel": "joule per square metre"
    },
    "Q64748823": {
        "factor": "3600000",
        "unit": "Q80374519",
        "label": "kilowatt-hour per square metre",
        "siLabel": "joule per square metre"
    },
    "Q64831044": {
        "factor": "0.025",
        "unit": "Q11573",
        "label": "metric inch",
        "siLabel": "metre"
    },
    "Q64833836": {
        "factor": "1",
        "unit": "Q64833836",
        "label": "lumen per square metre",
        "siLabel": "lumen per square metre"
    },
    "Q64866333": {
        "factor": "0.00025",
        "unit": "Q25517",
        "label": "metric cup",
        "siLabel": "cubic metre"
    },
    "Q64996135": {
        "factor": "0.00006309",
        "unit": "Q794261",
        "label": "gallon (US) per minute",
        "siLabel": "cubic metre per second"
    },
    "Q65028392": {
        "factor": "0.0000000000316887652",
        "unit": "Q182429",
        "label": "millimetre per year",
        "siLabel": "metre per second"
    },
    "Q65665675": {
        "factor": "1",
        "unit": "Q65665675",
        "label": "kilogram square metre per second",
        "siLabel": "kilogram square metre per second"
    },
    "Q65665809": {
        "factor": "1",
        "unit": "Q65665809",
        "label": "ampere second",
        "siLabel": "ampere second"
    },
    "Q65921799": {
        "factor": "0.00000000000333564",
        "unit": "Q28739766",
        "label": "statcoulomb-centimetre",
        "siLabel": "coulomb metre"
    },
    "Q67060736": {
        "factor": "1",
        "unit": "Q67060736",
        "label": "watt per kilogram",
        "siLabel": "watt per kilogram"
    },
    "Q67147153": {
        "factor": "1",
        "unit": "Q67147153",
        "label": "metre to the fourth power",
        "siLabel": "metre to the fourth power"
    },
    "Q67147815": {
        "factor": "1",
        "unit": "Q67147815",
        "label": "metre to the power of three",
        "siLabel": "metre to the power of three"
    },
    "Q67147817": {
        "factor": "1",
        "unit": "Q67147817",
        "label": "metre to the power of six",
        "siLabel": "metre to the power of six"
    },
    "Q68343206": {
        "factor": "1",
        "unit": "Q68343206",
        "label": "coulomb per square metre",
        "siLabel": "coulomb per square metre"
    },
    "Q68582988": {
        "factor": "1",
        "unit": "Q68582988",
        "label": "hertz per second",
        "siLabel": "hertz per second"
    },
    "Q68712008": {
        "factor": "1",
        "unit": "Q68712008",
        "label": "reciprocal mole",
        "siLabel": "reciprocal mole"
    },
    "Q68975544": {
        "factor": "1",
        "unit": "Q68975544",
        "label": "joule per kelvin difference",
        "siLabel": "joule per kelvin difference"
    },
    "Q69362731": {
        "factor": "1",
        "unit": "Q69362731",
        "label": "degree Celsius difference",
        "siLabel": "degree Celsius difference"
    },
    "Q69363953": {
        "factor": "1",
        "unit": "Q69363953",
        "label": "kelvin difference",
        "siLabel": "kelvin difference"
    },
    "Q69423273": {
        "factor": "1",
        "unit": "Q69423273",
        "label": "joule per kilogram kelvin difference",
        "siLabel": "joule per kilogram kelvin difference"
    },
    "Q69424806": {
        "factor": "1",
        "unit": "Q69424806",
        "label": "joule per cubic metre",
        "siLabel": "joule per cubic metre"
    },
    "Q69425409": {
        "factor": "1",
        "unit": "Q69425409",
        "label": "coulomb per cubic metre",
        "siLabel": "coulomb per cubic metre"
    },
    "Q69426951": {
        "factor": "1",
        "unit": "Q69426951",
        "label": "henry per metre",
        "siLabel": "henry per metre"
    },
    "Q69427692": {
        "factor": "1",
        "unit": "Q69427692",
        "label": "joule per mole kelvin difference",
        "siLabel": "joule per mole kelvin difference"
    },
    "Q69428896": {
        "factor": "1",
        "unit": "Q69428896",
        "label": "gray per second",
        "siLabel": "gray per second"
    },
    "Q69429226": {
        "factor": "1",
        "unit": "Q69429226",
        "label": "watt per square metre steradian",
        "siLabel": "watt per square metre steradian"
    },
    "Q69429606": {
        "factor": "1",
        "unit": "Q69429606",
        "label": "katal per cubic metre",
        "siLabel": "katal per cubic metre"
    },
    "Q69878540": {
        "factor": "0.00002841306",
        "unit": "Q25517",
        "label": "fluid ounce (UK)",
        "siLabel": "cubic metre"
    },
    "Q70103189": {
        "factor": "0.6987",
        "unit": "Q25343",
        "label": "square vara",
        "siLabel": "square metre"
    },
    "Q70277049": {
        "factor": "0.32483943186882723869591261039616",
        "unit": "Q11573",
        "label": "Paris foot",
        "siLabel": "metre"
    },
    "Q70280567": {
        "factor": "0.31385354274937454",
        "unit": "Q11573",
        "label": "Prussian foot",
        "siLabel": "metre"
    },
    "Q70304020": {
        "factor": "0.05496150027600473088",
        "unit": "Q25517",
        "label": "Q70304020",
        "siLabel": "cubic metre"
    },
    "Q70304109": {
        "factor": "0.00001789111337109529",
        "unit": "Q25517",
        "label": "Prussian cubic Inches",
        "siLabel": "cubic metre"
    },
    "Q70357954": {
        "factor": "0.03091584390525266112",
        "unit": "Q25517",
        "label": "Q70357954",
        "siLabel": "cubic metre"
    },
    "Q70378044": {
        "factor": "0.1",
        "unit": "Q41509",
        "label": "decimole",
        "siLabel": "mole"
    },
    "Q70378549": {
        "factor": "0.1",
        "unit": "Q11579",
        "label": "decikelvin",
        "siLabel": "kelvin"
    },
    "Q70379094": {
        "factor": "0.1",
        "unit": "Q83216",
        "label": "decicandela",
        "siLabel": "candela"
    },
    "Q70393458": {
        "factor": "1000",
        "unit": "Q41509",
        "label": "kilomole",
        "siLabel": "mole"
    },
    "Q70395375": {
        "factor": "1000000000000",
        "unit": "Q41509",
        "label": "teramole",
        "siLabel": "mole"
    },
    "Q70395643": {
        "factor": "1000000",
        "unit": "Q41509",
        "label": "megamole",
        "siLabel": "mole"
    },
    "Q70395830": {
        "factor": "1000",
        "unit": "Q11579",
        "label": "kilokelvin",
        "siLabel": "kelvin"
    },
    "Q70396179": {
        "factor": "0.001",
        "unit": "Q11579",
        "label": "millikelvin",
        "siLabel": "kelvin"
    },
    "Q70397275": {
        "factor": "0.000001",
        "unit": "Q11579",
        "label": "microkelvin",
        "siLabel": "kelvin"
    },
    "Q70397725": {
        "factor": "0.01",
        "unit": "Q41509",
        "label": "centimole",
        "siLabel": "mole"
    },
    "Q70397932": {
        "factor": "0.01",
        "unit": "Q11579",
        "label": "centikelvin",
        "siLabel": "kelvin"
    },
    "Q70398150": {
        "factor": "0.01",
        "unit": "Q83216",
        "label": "centicandela",
        "siLabel": "candela"
    },
    "Q70398457": {
        "factor": "0.000000001",
        "unit": "Q11579",
        "label": "nanokelvin",
        "siLabel": "kelvin"
    },
    "Q70398619": {
        "factor": "1000000",
        "unit": "Q11579",
        "label": "megakelvin",
        "siLabel": "kelvin"
    },
    "Q70398813": {
        "factor": "1000000000",
        "unit": "Q41509",
        "label": "gigamole",
        "siLabel": "mole"
    },
    "Q70398991": {
        "factor": "1000000000",
        "unit": "Q11579",
        "label": "gigakelvin",
        "siLabel": "kelvin"
    },
    "Q70420410": {
        "factor": "1.949036591212963432175475662377",
        "unit": "Q11573",
        "label": "Q70420410",
        "siLabel": "metre"
    },
    "Q70420742": {
        "factor": "1.1884461158997255804603932424332",
        "unit": "Q11573",
        "label": "Q70420742",
        "siLabel": "metre"
    },
    "Q70421135": {
        "factor": "1.1820545993004546741434597767194",
        "unit": "Q11573",
        "label": "Q70421135",
        "siLabel": "metre"
    },
    "Q70422268": {
        "factor": "0.105520656496862453465423639473599",
        "unit": "Q25343",
        "label": "Q70422268",
        "siLabel": "square metre"
    },
    "Q70422633": {
        "factor": "0.000732782336783767037954330829678",
        "unit": "Q25343",
        "label": "Q70422633",
        "siLabel": "square metre"
    },
    "Q70423709": {
        "factor": "2",
        "unit": "Q11573",
        "label": "Q70423709",
        "siLabel": "metre"
    },
    "Q70429730": {
        "factor": "0.28461047444988682834815491443275",
        "unit": "Q11573",
        "label": "Q70429730",
        "siLabel": "metre"
    },
    "Q70430606": {
        "factor": "0.02371753953749056902901290953606",
        "unit": "Q11573",
        "label": "Q70430606",
        "siLabel": "metre"
    },
    "Q70430939": {
        "factor": "0.00197646162812421408575107579467",
        "unit": "Q11573",
        "label": "Q70430939",
        "siLabel": "metre"
    },
    "Q70431791": {
        "factor": "0.5473093261112143378639049828772",
        "unit": "Q11573",
        "label": "Q70431791",
        "siLabel": "metre"
    },
    "Q70432710": {
        "factor": "0.69920108629193478552440417590362",
        "unit": "Q11573",
        "label": "Q70432710",
        "siLabel": "metre"
    },
    "Q70433308": {
        "factor": "0.68781005021440124368746750703239",
        "unit": "Q11573",
        "label": "Q70433308",
        "siLabel": "metre"
    },
    "Q70433823": {
        "factor": "0.69438015330688707238678587840586",
        "unit": "Q11573",
        "label": "Q70433823",
        "siLabel": "metre"
    },
    "Q70438872": {
        "factor": "10",
        "unit": "Q83216",
        "label": "decacandela",
        "siLabel": "candela"
    },
    "Q70439181": {
        "factor": "1000000",
        "unit": "Q83216",
        "label": "megacandela",
        "siLabel": "candela"
    },
    "Q70439298": {
        "factor": "100",
        "unit": "Q83216",
        "label": "hectocandela",
        "siLabel": "candela"
    },
    "Q70439504": {
        "factor": "0.000001",
        "unit": "Q83216",
        "label": "microcandela",
        "siLabel": "candela"
    },
    "Q70439642": {
        "factor": "0.000000001",
        "unit": "Q83216",
        "label": "nanocandela",
        "siLabel": "candela"
    },
    "Q70439816": {
        "factor": "0.000000000000001",
        "unit": "Q83216",
        "label": "femtocandela",
        "siLabel": "candela"
    },
    "Q70440025": {
        "factor": "10",
        "unit": "Q11579",
        "label": "decakelvin",
        "siLabel": "kelvin"
    },
    "Q70440438": {
        "factor": "100",
        "unit": "Q11579",
        "label": "hectokelvin",
        "siLabel": "kelvin"
    },
    "Q70440620": {
        "factor": "10",
        "unit": "Q41509",
        "label": "decamole",
        "siLabel": "mole"
    },
    "Q70440823": {
        "factor": "100",
        "unit": "Q41509",
        "label": "hectomole",
        "siLabel": "mole"
    },
    "Q70443020": {
        "factor": "1000000000000000000",
        "unit": "Q11579",
        "label": "exakelvin",
        "siLabel": "kelvin"
    },
    "Q70443154": {
        "factor": "0.000000000000000000000001",
        "unit": "Q11579",
        "label": "yoctokelvin",
        "siLabel": "kelvin"
    },
    "Q70443282": {
        "factor": "0.000000000000000000001",
        "unit": "Q11579",
        "label": "zeptokelvin",
        "siLabel": "kelvin"
    },
    "Q70443367": {
        "factor": "0.000000000000001",
        "unit": "Q11579",
        "label": "femtokelvin",
        "siLabel": "kelvin"
    },
    "Q70443453": {
        "factor": "1000000000000",
        "unit": "Q11579",
        "label": "terakelvin",
        "siLabel": "kelvin"
    },
    "Q70443757": {
        "factor": "0.000000000001",
        "unit": "Q11579",
        "label": "picokelvin",
        "siLabel": "kelvin"
    },
    "Q70443901": {
        "factor": "1000000000000000000000000",
        "unit": "Q11579",
        "label": "yottakelvin",
        "siLabel": "kelvin"
    },
    "Q70444029": {
        "factor": "1000000000000000",
        "unit": "Q11579",
        "label": "petakelvin",
        "siLabel": "kelvin"
    },
    "Q70444141": {
        "factor": "1000000000000000000",
        "unit": "Q41509",
        "label": "examole",
        "siLabel": "mole"
    },
    "Q70444284": {
        "factor": "0.000000000000000000000001",
        "unit": "Q41509",
        "label": "yoctomole",
        "siLabel": "mole"
    },
    "Q70444386": {
        "factor": "0.000000000000000000001",
        "unit": "Q41509",
        "label": "zeptomole",
        "siLabel": "mole"
    },
    "Q70444514": {
        "factor": "1000000000000000000000000",
        "unit": "Q41509",
        "label": "yottamole",
        "siLabel": "mole"
    },
    "Q70444609": {
        "factor": "1000000000000000",
        "unit": "Q41509",
        "label": "petamole",
        "siLabel": "mole"
    },
    "Q70444756": {
        "factor": "1000000000000000000",
        "unit": "Q83216",
        "label": "exacandela",
        "siLabel": "candela"
    },
    "Q70444855": {
        "factor": "0.000000000000000000000001",
        "unit": "Q83216",
        "label": "yoctocandela",
        "siLabel": "candela"
    },
    "Q70445013": {
        "factor": "0.000000000000000000001",
        "unit": "Q83216",
        "label": "zeptocandela",
        "siLabel": "candela"
    },
    "Q70445131": {
        "factor": "1000000000000",
        "unit": "Q83216",
        "label": "teracandela",
        "siLabel": "candela"
    },
    "Q70445211": {
        "factor": "1000000000",
        "unit": "Q83216",
        "label": "gigacandela",
        "siLabel": "candela"
    },
    "Q70445288": {
        "factor": "0.000000000001",
        "unit": "Q83216",
        "label": "picocandela",
        "siLabel": "candela"
    },
    "Q70445374": {
        "factor": "1000000000000000000000000",
        "unit": "Q83216",
        "label": "yottacandela",
        "siLabel": "candela"
    },
    "Q70445449": {
        "factor": "1000000000000000",
        "unit": "Q83216",
        "label": "petacandela",
        "siLabel": "candela"
    },
    "Q70447331": {
        "factor": "0.70065496833248658521426192366334",
        "unit": "Q11573",
        "label": "Q70447331",
        "siLabel": "metre"
    },
    "Q70447934": {
        "factor": "0.68020000977405757223093513764926",
        "unit": "Q11573",
        "label": "Q70447934",
        "siLabel": "metre"
    },
    "Q70448574": {
        "factor": "0.69443903045391329732379951256649",
        "unit": "Q11573",
        "label": "Q70448574",
        "siLabel": "metre"
    },
    "Q70459229": {
        "factor": "0.69141170741524686569650843810016",
        "unit": "Q11573",
        "label": "Q70459229",
        "siLabel": "metre"
    },
    "Q70459877": {
        "factor": "0.54379023226596870944469926293124",
        "unit": "Q11573",
        "label": "Q70459877",
        "siLabel": "metre"
    },
    "Q70462704": {
        "factor": "0.69470521832169469742217532984445",
        "unit": "Q11573",
        "label": "Q70462704",
        "siLabel": "metre"
    },
    "Q71367465": {
        "factor": "0.6877707987830504270627917509253",
        "unit": "Q11573",
        "label": "Q71367465",
        "siLabel": "metre"
    },
    "Q71368780": {
        "factor": "0.69431270400818653117541776877356",
        "unit": "Q11573",
        "label": "Q71368780",
        "siLabel": "metre"
    },
    "Q71369143": {
        "factor": "0.69028379272125788222881429709184",
        "unit": "Q11573",
        "label": "Q71369143",
        "siLabel": "metre"
    },
    "Q71369646": {
        "factor": "0.6856006909118156228709482236253",
        "unit": "Q11573",
        "label": "Q71369646",
        "siLabel": "metre"
    },
    "Q71370174": {
        "factor": "0.69499847614213183312377580650662",
        "unit": "Q11573",
        "label": "Q71370174",
        "siLabel": "metre"
    },
    "Q71373934": {
        "factor": "0.66400338035131456743154081159798",
        "unit": "Q11573",
        "label": "Q71373934",
        "siLabel": "metre"
    },
    "Q71374883": {
        "factor": "0.57314308426233801520797158853176",
        "unit": "Q11573",
        "label": "Q71374883",
        "siLabel": "metre"
    },
    "Q71580762": {
        "factor": "1",
        "unit": "Q71580762",
        "label": "weber metre",
        "siLabel": "weber metre"
    },
    "Q71581529": {
        "factor": "1",
        "unit": "Q71581529",
        "label": "ampere square metre",
        "siLabel": "ampere square metre"
    },
    "Q71788569": {
        "factor": "0.2886897659264803185563153910795",
        "unit": "Q11573",
        "label": "Q71788569",
        "siLabel": "metre"
    },
    "Q71788932": {
        "factor": "0.2821004882841966771380462193089",
        "unit": "Q11573",
        "label": "Q71788932",
        "siLabel": "metre"
    },
    "Q71792383": {
        "factor": "4.6190362548236850969010462572721",
        "unit": "Q11573",
        "label": "Q71792383",
        "siLabel": "metre"
    },
    "Q71792864": {
        "factor": "4.5136078125471468342087395089424",
        "unit": "Q11573",
        "label": "Q71792864",
        "siLabel": "metre"
    },
    "Q72081071": {
        "factor": "0.000000000000160217656535",
        "unit": "Q25269",
        "label": "megaelectronvolt",
        "siLabel": "joule"
    },
    "Q73359822": {
        "factor": "0.0000000316887652",
        "unit": "Q182429",
        "label": "metre per year",
        "siLabel": "metre per second"
    },
    "Q73429216": {
        "factor": "1",
        "unit": "Q73429216",
        "label": "newton metre second",
        "siLabel": "newton metre second"
    },
    "Q77899731": {
        "factor": "1",
        "unit": "Q77899731",
        "label": "weber per metre",
        "siLabel": "weber per metre"
    },
    "Q77996931": {
        "factor": "1",
        "unit": "Q77996931",
        "label": "reciprocal henry",
        "siLabel": "reciprocal henry"
    },
    "Q78336909": {
        "factor": "1",
        "unit": "Q78336909",
        "label": "cubic metre per kilogram square second",
        "siLabel": "cubic metre per kilogram square second"
    },
    "Q78775089": {
        "factor": "1",
        "unit": "Q78775089",
        "label": "kilogram metre per second",
        "siLabel": "kilogram metre per second"
    },
    "Q79104611": {
        "factor": "1",
        "unit": "Q79104611",
        "label": "reciprocal pascal",
        "siLabel": "reciprocal pascal"
    },
    "Q79331235": {
        "factor": "1",
        "unit": "Q79331235",
        "label": "reciprocal kelvin difference",
        "siLabel": "reciprocal kelvin difference"
    },
    "Q79398638": {
        "factor": "1",
        "unit": "Q79398638",
        "label": "pascal per kelvin difference",
        "siLabel": "pascal per kelvin difference"
    },
    "Q80026587": {
        "factor": "0.0000000000000000000324078",
        "unit": "Q6137407",
        "label": "kilometre per second megaparsec",
        "siLabel": "reciprocal second"
    },
    "Q80117150": {
        "factor": "1",
        "unit": "Q80117150",
        "label": "coulomb per metre",
        "siLabel": "coulomb per metre"
    },
    "Q80237579": {
        "factor": "1000000000",
        "unit": "Q56023789",
        "label": "joule per nanometre",
        "siLabel": "joule per metre"
    },
    "Q80374519": {
        "factor": "1",
        "unit": "Q80374519",
        "label": "joule per square metre",
        "siLabel": "joule per square metre"
    },
    "Q80842107": {
        "factor": "1",
        "unit": "Q80842107",
        "label": "siemens per metre",
        "siLabel": "siemens per metre"
    },
    "Q81062869": {
        "factor": "1000000000",
        "unit": "Q96192470",
        "label": "watt per nanometre",
        "siLabel": "watt per metre"
    },
    "Q81073100": {
        "factor": "1000000000",
        "unit": "Q100294053",
        "label": "watt per steradian nanometre",
        "siLabel": "watt per steradian metre"
    },
    "Q81663366": {
        "factor": "1",
        "unit": "Q81663366",
        "label": "watt per kelvin",
        "siLabel": "watt per kelvin"
    },
    "Q82966924": {
        "factor": "1",
        "unit": "Q82966924",
        "label": "reciprocal square metre",
        "siLabel": "reciprocal square metre"
    },
    "Q83386886": {
        "factor": "1",
        "unit": "Q83386886",
        "label": "lumen per watt",
        "siLabel": "lumen per watt"
    },
    "Q83620455": {
        "factor": "1",
        "unit": "Q83620455",
        "label": "lux second",
        "siLabel": "lux second"
    },
    "Q83853845": {
        "factor": "1",
        "unit": "Q83853845",
        "label": "per second steradian",
        "siLabel": "per second steradian"
    },
    "Q83855084": {
        "factor": "1",
        "unit": "Q83855084",
        "label": "per square metre second steradian",
        "siLabel": "per square metre second steradian"
    },
    "Q83948162": {
        "factor": "1",
        "unit": "Q83948162",
        "label": "volt metre",
        "siLabel": "volt metre"
    },
    "Q83951055": {
        "factor": "1",
        "unit": "Q83951055",
        "label": "per square metre second",
        "siLabel": "per square metre second"
    },
    "Q84451486": {
        "factor": "1",
        "unit": "Q84451486",
        "label": "kelvin metre per watt",
        "siLabel": "kelvin metre per watt"
    },
    "Q85178038": {
        "factor": "1",
        "unit": "Q85178038",
        "label": "mole per second",
        "siLabel": "mole per second"
    },
    "Q85854198": {
        "factor": "1000000",
        "unit": "Q12438",
        "label": "meganewton",
        "siLabel": "newton"
    },
    "Q86200529": {
        "factor": "1",
        "unit": "Q86200529",
        "label": "square metre per kilogram",
        "siLabel": "square metre per kilogram"
    },
    "Q86203731": {
        "factor": "1",
        "unit": "Q86203731",
        "label": "square metre per mole",
        "siLabel": "square metre per mole"
    },
    "Q86300471": {
        "factor": "152",
        "unit": "Q11573",
        "label": "Q86300471",
        "siLabel": "metre"
    },
    "Q86897783": {
        "factor": "1",
        "unit": "Q86897783",
        "label": "square pascal second",
        "siLabel": "square pascal second"
    },
    "Q87047886": {
        "factor": "1",
        "unit": "Q87047886",
        "label": "pascal second per cubic metre",
        "siLabel": "pascal second per cubic metre"
    },
    "Q87049028": {
        "factor": "1",
        "unit": "Q87049028",
        "label": "newton second per metre",
        "siLabel": "newton second per metre"
    },
    "Q87051580": {
        "factor": "1",
        "unit": "Q87051580",
        "label": "pascal second per metre",
        "siLabel": "pascal second per metre"
    },
    "Q87262709": {
        "factor": "1000",
        "unit": "Q47083",
        "label": "kiloohm",
        "siLabel": "ohm"
    },
    "Q87416053": {
        "factor": "1000000",
        "unit": "Q47083",
        "label": "megaohm",
        "siLabel": "ohm"
    },
    "Q87416237": {
        "factor": "0.29307222",
        "unit": "Q25236",
        "label": "BTUH",
        "siLabel": "watt"
    },
    "Q87546229": {
        "factor": "0.000000000001",
        "unit": "Q86897783",
        "label": "square micropascal second",
        "siLabel": "square pascal second"
    },
    "Q87596952": {
        "factor": "0.048",
        "unit": "Q11573",
        "label": "Open Rack rack unit",
        "siLabel": "metre"
    },
    "Q88768297": {
        "factor": "1",
        "unit": "Q88768297",
        "label": "becquerel per kilogram",
        "siLabel": "becquerel per kilogram"
    },
    "Q88957663": {
        "factor": "1",
        "unit": "Q88957663",
        "label": "mole per kilogram",
        "siLabel": "mole per kilogram"
    },
    "Q89187604": {
        "factor": "0.1589873",
        "unit": "Q25517",
        "label": "barrel (US) for petroleum",
        "siLabel": "cubic metre"
    },
    "Q89473028": {
        "factor": "0.03636872",
        "unit": "Q25517",
        "label": "bushel (UK)",
        "siLabel": "cubic metre"
    },
    "Q89662131": {
        "factor": "0.00056826125",
        "unit": "Q25517",
        "label": "pint (UK)",
        "siLabel": "cubic metre"
    },
    "Q89992008": {
        "factor": "1",
        "unit": "Q89992008",
        "label": "reciprocal farad",
        "siLabel": "reciprocal farad"
    },
    "Q90781124": {
        "factor": "1",
        "unit": "Q199",
        "label": "uno",
        "siLabel": "1"
    },
    "Q92011107": {
        "factor": "1",
        "unit": "Q92011107",
        "label": "kilogram per square metre second",
        "siLabel": "kilogram per square metre second"
    },
    "Q92711514": {
        "factor": "1",
        "unit": "Q92711514",
        "label": "joule per second",
        "siLabel": "joule per second"
    },
    "Q92717607": {
        "factor": "1",
        "unit": "Q92717607",
        "label": "kelvin difference per metre",
        "siLabel": "kelvin difference per metre"
    },
    "Q92896481": {
        "factor": "1",
        "unit": "Q92896481",
        "label": "metre per kilogram",
        "siLabel": "metre per kilogram"
    },
    "Q93678895": {
        "factor": "0.000118",
        "unit": "Q25517",
        "label": "gill (US)",
        "siLabel": "cubic metre"
    },
    "Q93679498": {
        "factor": "0.000142",
        "unit": "Q25517",
        "label": "gill (UK)",
        "siLabel": "cubic metre"
    },
    "Q93811434": {
        "factor": "4.19",
        "unit": "Q25269",
        "label": "calorie (mean)",
        "siLabel": "joule"
    },
    "Q93814649": {
        "factor": "4.1868",
        "unit": "Q25269",
        "label": "calorie (international table)",
        "siLabel": "joule"
    },
    "Q93947085": {
        "factor": "1",
        "unit": "Q93947085",
        "label": "kelvin per pascal",
        "siLabel": "kelvin per pascal"
    },
    "Q94076025": {
        "factor": "10",
        "unit": "Q484092",
        "label": "decalumen",
        "siLabel": "lumen"
    },
    "Q94076717": {
        "factor": "10",
        "unit": "Q208634",
        "label": "decakatal",
        "siLabel": "katal"
    },
    "Q94414053": {
        "factor": "1000000000000000",
        "unit": "Q33680",
        "label": "petaradian",
        "siLabel": "radian"
    },
    "Q94414499": {
        "factor": "1000000000000000",
        "unit": "Q25406",
        "label": "petacoulomb",
        "siLabel": "coulomb"
    },
    "Q94415026": {
        "factor": "1000000000",
        "unit": "Q33680",
        "label": "gigaradian",
        "siLabel": "radian"
    },
    "Q94415255": {
        "factor": "1000000000",
        "unit": "Q25406",
        "label": "gigacoulomb",
        "siLabel": "coulomb"
    },
    "Q94415438": {
        "factor": "1000000000000000000000000",
        "unit": "Q33680",
        "label": "yottaradian",
        "siLabel": "radian"
    },
    "Q94415526": {
        "factor": "1000000000000000000000000",
        "unit": "Q25406",
        "label": "yottacoulomb",
        "siLabel": "coulomb"
    },
    "Q94415561": {
        "factor": "1000",
        "unit": "Q33680",
        "label": "kiloradian",
        "siLabel": "radian"
    },
    "Q94415782": {
        "factor": "1000000",
        "unit": "Q33680",
        "label": "megaradian",
        "siLabel": "radian"
    },
    "Q94416260": {
        "factor": "1000000000",
        "unit": "Q12438",
        "label": "giganewton",
        "siLabel": "newton"
    },
    "Q94416535": {
        "factor": "0.01",
        "unit": "Q12438",
        "label": "centinewton",
        "siLabel": "newton"
    },
    "Q94416879": {
        "factor": "1000000000000000000000000",
        "unit": "Q12438",
        "label": "yottanewton",
        "siLabel": "newton"
    },
    "Q94417138": {
        "factor": "1000000000000000",
        "unit": "Q12438",
        "label": "petanewton",
        "siLabel": "newton"
    },
    "Q94417481": {
        "factor": "0.000001",
        "unit": "Q190095",
        "label": "microgray",
        "siLabel": "gray"
    },
    "Q94417583": {
        "factor": "0.000001",
        "unit": "Q169893",
        "label": "microsiemens",
        "siLabel": "siemens"
    },
    "Q94417598": {
        "factor": "0.000001",
        "unit": "Q163343",
        "label": "microtesla",
        "siLabel": "tesla"
    },
    "Q94417933": {
        "factor": "0.000001",
        "unit": "Q484092",
        "label": "microlumen",
        "siLabel": "lumen"
    },
    "Q94418102": {
        "factor": "0.000001",
        "unit": "Q12438",
        "label": "micronewton",
        "siLabel": "newton"
    },
    "Q94418220": {
        "factor": "0.000001",
        "unit": "Q177612",
        "label": "microsteradian",
        "siLabel": "steradian"
    },
    "Q94418481": {
        "factor": "0.000001",
        "unit": "Q102573",
        "label": "microbecquerel",
        "siLabel": "becquerel"
    },
    "Q94479580": {
        "factor": "1000000000",
        "unit": "Q47083",
        "label": "gigaohm",
        "siLabel": "ohm"
    },
    "Q94480021": {
        "factor": "1000000000000000",
        "unit": "Q47083",
        "label": "petaohm",
        "siLabel": "ohm"
    },
    "Q94480081": {
        "factor": "1000000000000000000000000",
        "unit": "Q47083",
        "label": "yottaohm",
        "siLabel": "ohm"
    },
    "Q94480128": {
        "factor": "0.01",
        "unit": "Q47083",
        "label": "centiohm",
        "siLabel": "ohm"
    },
    "Q94480131": {
        "factor": "1000000000000",
        "unit": "Q47083",
        "label": "teraohm",
        "siLabel": "ohm"
    },
    "Q94480136": {
        "factor": "0.000000000001",
        "unit": "Q47083",
        "label": "picoohm",
        "siLabel": "ohm"
    },
    "Q94480254": {
        "factor": "0.000000001",
        "unit": "Q47083",
        "label": "nanoohm",
        "siLabel": "ohm"
    },
    "Q94480476": {
        "factor": "0.1",
        "unit": "Q47083",
        "label": "deciohm",
        "siLabel": "ohm"
    },
    "Q94480633": {
        "factor": "1000000000000000000",
        "unit": "Q47083",
        "label": "exaohm",
        "siLabel": "ohm"
    },
    "Q94480967": {
        "factor": "10",
        "unit": "Q47083",
        "label": "decaohm",
        "siLabel": "ohm"
    },
    "Q94481176": {
        "factor": "100",
        "unit": "Q47083",
        "label": "hectoohm",
        "siLabel": "ohm"
    },
    "Q94481339": {
        "factor": "0.000000000000001",
        "unit": "Q47083",
        "label": "femtoohm",
        "siLabel": "ohm"
    },
    "Q94481646": {
        "factor": "0.000000000000000000000001",
        "unit": "Q47083",
        "label": "yoctoohm",
        "siLabel": "ohm"
    },
    "Q94487174": {
        "factor": "0.000000000000000000001",
        "unit": "Q47083",
        "label": "zeptoohm",
        "siLabel": "ohm"
    },
    "Q94487366": {
        "factor": "0.001",
        "unit": "Q47083",
        "label": "milliohm",
        "siLabel": "ohm"
    },
    "Q94487561": {
        "factor": "0.000001",
        "unit": "Q47083",
        "label": "microohm",
        "siLabel": "ohm"
    },
    "Q94487750": {
        "factor": "1000",
        "unit": "Q190095",
        "label": "kilogray",
        "siLabel": "gray"
    },
    "Q94488007": {
        "factor": "1000",
        "unit": "Q179836",
        "label": "kilolux",
        "siLabel": "lux"
    },
    "Q94488361": {
        "factor": "1000000",
        "unit": "Q131255",
        "label": "megafarad",
        "siLabel": "farad"
    },
    "Q94488759": {
        "factor": "1000000000",
        "unit": "Q102573",
        "label": "gigabecquerel",
        "siLabel": "becquerel"
    },
    "Q94489041": {
        "factor": "1000000000000000",
        "unit": "Q102573",
        "label": "petabecquerel",
        "siLabel": "becquerel"
    },
    "Q94489223": {
        "factor": "1000000000000000000000000",
        "unit": "Q102573",
        "label": "yottabecquerel",
        "siLabel": "becquerel"
    },
    "Q94489429": {
        "factor": "1000000",
        "unit": "Q102573",
        "label": "megabecquerel",
        "siLabel": "becquerel"
    },
    "Q94489465": {
        "factor": "1000",
        "unit": "Q102573",
        "label": "kilobecquerel",
        "siLabel": "becquerel"
    },
    "Q94489476": {
        "factor": "1000000000000",
        "unit": "Q102573",
        "label": "terabecquerel",
        "siLabel": "becquerel"
    },
    "Q94489494": {
        "factor": "1000",
        "unit": "Q170804",
        "label": "kiloweber",
        "siLabel": "weber"
    },
    "Q94489520": {
        "factor": "1000",
        "unit": "Q169893",
        "label": "kilosiemens",
        "siLabel": "siemens"
    },
    "Q94490951": {
        "factor": "1000",
        "unit": "Q484092",
        "label": "kilolumen",
        "siLabel": "lumen"
    },
    "Q94491129": {
        "factor": "1000",
        "unit": "Q208634",
        "label": "kilokatal",
        "siLabel": "katal"
    },
    "Q94634634": {
        "factor": "0.01",
        "unit": "Q25406",
        "label": "centicoulomb",
        "siLabel": "coulomb"
    },
    "Q94634655": {
        "factor": "1000000",
        "unit": "Q25406",
        "label": "megacoulomb",
        "siLabel": "coulomb"
    },
    "Q94634666": {
        "factor": "1000",
        "unit": "Q25406",
        "label": "kilocoulomb",
        "siLabel": "coulomb"
    },
    "Q94634677": {
        "factor": "1000000000000",
        "unit": "Q25406",
        "label": "teracoulomb",
        "siLabel": "coulomb"
    },
    "Q94634684": {
        "factor": "0.000001",
        "unit": "Q25406",
        "label": "microcoulomb",
        "siLabel": "coulomb"
    },
    "Q94634699": {
        "factor": "0.001",
        "unit": "Q25406",
        "label": "millicoulomb",
        "siLabel": "coulomb"
    },
    "Q94693759": {
        "factor": "0.01",
        "unit": "Q177612",
        "label": "centisteradian",
        "siLabel": "steradian"
    },
    "Q94693773": {
        "factor": "0.001",
        "unit": "Q177612",
        "label": "millisteradian",
        "siLabel": "steradian"
    },
    "Q94693786": {
        "factor": "0.001",
        "unit": "Q170804",
        "label": "milliweber",
        "siLabel": "weber"
    },
    "Q94693805": {
        "factor": "0.000001",
        "unit": "Q170804",
        "label": "microweber",
        "siLabel": "weber"
    },
    "Q94693819": {
        "factor": "1000000000",
        "unit": "Q169893",
        "label": "gigasiemens",
        "siLabel": "siemens"
    },
    "Q94693849": {
        "factor": "0.01",
        "unit": "Q169893",
        "label": "centisiemens",
        "siLabel": "siemens"
    },
    "Q94693918": {
        "factor": "1000000",
        "unit": "Q169893",
        "label": "megasiemens",
        "siLabel": "siemens"
    },
    "Q94694019": {
        "factor": "1000000000000",
        "unit": "Q169893",
        "label": "terasiemens",
        "siLabel": "siemens"
    },
    "Q94694096": {
        "factor": "0.000000000001",
        "unit": "Q169893",
        "label": "picosiemens",
        "siLabel": "siemens"
    },
    "Q94694154": {
        "factor": "0.000000001",
        "unit": "Q169893",
        "label": "nanosiemens",
        "siLabel": "siemens"
    },
    "Q94694206": {
        "factor": "0.001",
        "unit": "Q169893",
        "label": "millisiemens",
        "siLabel": "siemens"
    },
    "Q94731530": {
        "factor": "0.001",
        "unit": "Q484092",
        "label": "millilumen",
        "siLabel": "lumen"
    },
    "Q94731808": {
        "factor": "0.001",
        "unit": "Q208634",
        "label": "millikatal",
        "siLabel": "katal"
    },
    "Q94731887": {
        "factor": "0.000001",
        "unit": "Q208634",
        "label": "microkatal",
        "siLabel": "katal"
    },
    "Q94732218": {
        "factor": "0.000000001",
        "unit": "Q208634",
        "label": "nanokatal",
        "siLabel": "katal"
    },
    "Q94732627": {
        "factor": "0.000000000001",
        "unit": "Q208634",
        "label": "picokatal",
        "siLabel": "katal"
    },
    "Q94733432": {
        "factor": "0.000000000000001",
        "unit": "Q208634",
        "label": "femtokatal",
        "siLabel": "katal"
    },
    "Q94733760": {
        "factor": "0.01",
        "unit": "Q190095",
        "label": "centigray",
        "siLabel": "gray"
    },
    "Q94734107": {
        "factor": "0.1",
        "unit": "Q190095",
        "label": "decigray",
        "siLabel": "gray"
    },
    "Q94734232": {
        "factor": "0.001",
        "unit": "Q190095",
        "label": "milligray",
        "siLabel": "gray"
    },
    "Q94734359": {
        "factor": "10",
        "unit": "Q190095",
        "label": "decagray",
        "siLabel": "gray"
    },
    "Q94734468": {
        "factor": "0.000000000000000001",
        "unit": "Q190095",
        "label": "attogray",
        "siLabel": "gray"
    },
    "Q94734527": {
        "factor": "0.000000000001",
        "unit": "Q190095",
        "label": "picogray",
        "siLabel": "gray"
    },
    "Q94734593": {
        "factor": "0.000000001",
        "unit": "Q190095",
        "label": "nanogray",
        "siLabel": "gray"
    },
    "Q94734689": {
        "factor": "1000",
        "unit": "Q163343",
        "label": "kilotesla",
        "siLabel": "tesla"
    },
    "Q94734788": {
        "factor": "0.001",
        "unit": "Q163343",
        "label": "millitesla",
        "siLabel": "tesla"
    },
    "Q94939947": {
        "factor": "1000000000",
        "unit": "Q208634",
        "label": "gigakatal",
        "siLabel": "katal"
    },
    "Q94940018": {
        "factor": "1000000000000000",
        "unit": "Q208634",
        "label": "petakatal",
        "siLabel": "katal"
    },
    "Q94940081": {
        "factor": "0.000000000000000000000001",
        "unit": "Q208634",
        "label": "yoctokatal",
        "siLabel": "katal"
    },
    "Q94940160": {
        "factor": "0.1",
        "unit": "Q208634",
        "label": "decikatal",
        "siLabel": "katal"
    },
    "Q94940232": {
        "factor": "1000000000000000000",
        "unit": "Q208634",
        "label": "exakatal",
        "siLabel": "katal"
    },
    "Q94940295": {
        "factor": "1000000000000000000000000",
        "unit": "Q208634",
        "label": "yottakatal",
        "siLabel": "katal"
    },
    "Q94940582": {
        "factor": "1000000000000",
        "unit": "Q208634",
        "label": "terakatal",
        "siLabel": "katal"
    },
    "Q94940892": {
        "factor": "100",
        "unit": "Q208634",
        "label": "hectokatal",
        "siLabel": "katal"
    },
    "Q94941461": {
        "factor": "0.000000000000000000001",
        "unit": "Q208634",
        "label": "zeptokatal",
        "siLabel": "katal"
    },
    "Q94942602": {
        "factor": "1000000",
        "unit": "Q190095",
        "label": "megagray",
        "siLabel": "gray"
    },
    "Q94942863": {
        "factor": "1000000000",
        "unit": "Q190095",
        "label": "gigagray",
        "siLabel": "gray"
    },
    "Q94986863": {
        "factor": "1000000000000000000000000",
        "unit": "Q170804",
        "label": "yottaweber",
        "siLabel": "weber"
    },
    "Q94986889": {
        "factor": "1000000000000000",
        "unit": "Q170804",
        "label": "petaweber",
        "siLabel": "weber"
    },
    "Q94986906": {
        "factor": "0.01",
        "unit": "Q170804",
        "label": "centiweber",
        "siLabel": "weber"
    },
    "Q94986920": {
        "factor": "1000000000",
        "unit": "Q170804",
        "label": "gigaweber",
        "siLabel": "weber"
    },
    "Q94986942": {
        "factor": "1000000",
        "unit": "Q170804",
        "label": "megaweber",
        "siLabel": "weber"
    },
    "Q94986962": {
        "factor": "1000000000000",
        "unit": "Q170804",
        "label": "teraweber",
        "siLabel": "weber"
    },
    "Q95178536": {
        "factor": "1000000",
        "unit": "Q484092",
        "label": "megalumen",
        "siLabel": "lumen"
    },
    "Q95178777": {
        "factor": "1000000000000",
        "unit": "Q484092",
        "label": "teralumen",
        "siLabel": "lumen"
    },
    "Q95178881": {
        "factor": "0.01",
        "unit": "Q484092",
        "label": "centilumen",
        "siLabel": "lumen"
    },
    "Q95179024": {
        "factor": "0.000000000001",
        "unit": "Q484092",
        "label": "picolumen",
        "siLabel": "lumen"
    },
    "Q95179137": {
        "factor": "0.000000001",
        "unit": "Q484092",
        "label": "nanolumen",
        "siLabel": "lumen"
    },
    "Q95179382": {
        "factor": "100",
        "unit": "Q484092",
        "label": "hectolumen",
        "siLabel": "lumen"
    },
    "Q95179467": {
        "factor": "0.000000000000001",
        "unit": "Q484092",
        "label": "femtolumen",
        "siLabel": "lumen"
    },
    "Q95179608": {
        "factor": "0.000000000000000000001",
        "unit": "Q484092",
        "label": "zeptolumen",
        "siLabel": "lumen"
    },
    "Q95179695": {
        "factor": "1000000",
        "unit": "Q208634",
        "label": "megakatal",
        "siLabel": "katal"
    },
    "Q95179788": {
        "factor": "0.01",
        "unit": "Q208634",
        "label": "centikatal",
        "siLabel": "katal"
    },
    "Q95179882": {
        "factor": "1000000000000000",
        "unit": "Q190095",
        "label": "petagray",
        "siLabel": "gray"
    },
    "Q95375885": {
        "factor": "1",
        "unit": "Q95375885",
        "label": "watt per square metre hertz",
        "siLabel": "watt per square metre hertz"
    },
    "Q95377836": {
        "factor": "1000000000000000",
        "unit": "Q131255",
        "label": "petafarad",
        "siLabel": "farad"
    },
    "Q95377853": {
        "factor": "1000000000000000000000000",
        "unit": "Q131255",
        "label": "yottafarad",
        "siLabel": "farad"
    },
    "Q95378017": {
        "factor": "1000",
        "unit": "Q131255",
        "label": "kilofarad",
        "siLabel": "farad"
    },
    "Q95378296": {
        "factor": "1000000000000",
        "unit": "Q131255",
        "label": "terafarad",
        "siLabel": "farad"
    },
    "Q95379145": {
        "factor": "0.01",
        "unit": "Q131255",
        "label": "centifarad",
        "siLabel": "farad"
    },
    "Q95379382": {
        "factor": "1000000000",
        "unit": "Q131255",
        "label": "gigafarad",
        "siLabel": "farad"
    },
    "Q95379491": {
        "factor": "10",
        "unit": "Q25406",
        "label": "decacoulomb",
        "siLabel": "coulomb"
    },
    "Q95379580": {
        "factor": "100",
        "unit": "Q25406",
        "label": "hectocoulomb",
        "siLabel": "coulomb"
    },
    "Q95379588": {
        "factor": "0.1",
        "unit": "Q25406",
        "label": "decicoulomb",
        "siLabel": "coulomb"
    },
    "Q95379596": {
        "factor": "1000000000000000000",
        "unit": "Q25406",
        "label": "exacoulomb",
        "siLabel": "coulomb"
    },
    "Q95445986": {
        "factor": "0.000000001",
        "unit": "Q25406",
        "label": "nanocoulomb",
        "siLabel": "coulomb"
    },
    "Q95446327": {
        "factor": "0.000000000001",
        "unit": "Q25406",
        "label": "picocoulomb",
        "siLabel": "coulomb"
    },
    "Q95446670": {
        "factor": "0.000000000000001",
        "unit": "Q25406",
        "label": "femtocoulomb",
        "siLabel": "coulomb"
    },
    "Q95447079": {
        "factor": "0.000000000000000000001",
        "unit": "Q25406",
        "label": "zeptocoulomb",
        "siLabel": "coulomb"
    },
    "Q95447237": {
        "factor": "0.000000000000000000000001",
        "unit": "Q25406",
        "label": "yoctocoulomb",
        "siLabel": "coulomb"
    },
    "Q95447253": {
        "factor": "0.000000000000001",
        "unit": "Q131255",
        "label": "femtofarad",
        "siLabel": "farad"
    },
    "Q95447263": {
        "factor": "0.000000000000000000001",
        "unit": "Q131255",
        "label": "zeptofarad",
        "siLabel": "farad"
    },
    "Q95447276": {
        "factor": "0.000000000000000001",
        "unit": "Q131255",
        "label": "attofarad",
        "siLabel": "farad"
    },
    "Q95447555": {
        "factor": "0.1",
        "unit": "Q131255",
        "label": "decifarad",
        "siLabel": "farad"
    },
    "Q95447863": {
        "factor": "1000000000000000000",
        "unit": "Q131255",
        "label": "exafarad",
        "siLabel": "farad"
    },
    "Q95448262": {
        "factor": "0.000000000000000000000001",
        "unit": "Q131255",
        "label": "yoctofarad",
        "siLabel": "farad"
    },
    "Q95448479": {
        "factor": "100",
        "unit": "Q131255",
        "label": "hectofarad",
        "siLabel": "farad"
    },
    "Q95448689": {
        "factor": "10",
        "unit": "Q131255",
        "label": "decafarad",
        "siLabel": "farad"
    },
    "Q95448950": {
        "factor": "1000",
        "unit": "Q103246",
        "label": "kilosievert",
        "siLabel": "sievert"
    },
    "Q95559229": {
        "factor": "1000000000",
        "unit": "Q103246",
        "label": "gigasievert",
        "siLabel": "sievert"
    },
    "Q95559368": {
        "factor": "1000000000000000000000000",
        "unit": "Q103246",
        "label": "yottasievert",
        "siLabel": "sievert"
    },
    "Q95559441": {
        "factor": "1000000",
        "unit": "Q103246",
        "label": "megasievert",
        "siLabel": "sievert"
    },
    "Q95559576": {
        "factor": "1000000000000",
        "unit": "Q103246",
        "label": "terasievert",
        "siLabel": "sievert"
    },
    "Q95559603": {
        "factor": "1000000000000000",
        "unit": "Q103246",
        "label": "petasievert",
        "siLabel": "sievert"
    },
    "Q95609154": {
        "factor": "0.000000001",
        "unit": "Q170804",
        "label": "nanoweber",
        "siLabel": "weber"
    },
    "Q95609210": {
        "factor": "0.000000000000001",
        "unit": "Q170804",
        "label": "femtoweber",
        "siLabel": "weber"
    },
    "Q95609261": {
        "factor": "0.000000000000000000001",
        "unit": "Q170804",
        "label": "zeptoweber",
        "siLabel": "weber"
    },
    "Q95609291": {
        "factor": "0.1",
        "unit": "Q170804",
        "label": "deciweber",
        "siLabel": "weber"
    },
    "Q95609317": {
        "factor": "1000000000000000000",
        "unit": "Q170804",
        "label": "exaweber",
        "siLabel": "weber"
    },
    "Q95676212": {
        "factor": "0.000000000001",
        "unit": "Q170804",
        "label": "picoweber",
        "siLabel": "weber"
    },
    "Q95676232": {
        "factor": "0.000000000000000000000001",
        "unit": "Q170804",
        "label": "yoctoweber",
        "siLabel": "weber"
    },
    "Q95676243": {
        "factor": "100",
        "unit": "Q170804",
        "label": "hectoweber",
        "siLabel": "weber"
    },
    "Q95676250": {
        "factor": "10",
        "unit": "Q170804",
        "label": "decaweber",
        "siLabel": "weber"
    },
    "Q95676257": {
        "factor": "1000000000000000",
        "unit": "Q169893",
        "label": "petasiemens",
        "siLabel": "siemens"
    },
    "Q95676260": {
        "factor": "1000000000000000000000000",
        "unit": "Q169893",
        "label": "yottasiemens",
        "siLabel": "siemens"
    },
    "Q95676273": {
        "factor": "0.000000000000000000001",
        "unit": "Q169893",
        "label": "zeptosiemens",
        "siLabel": "siemens"
    },
    "Q95676275": {
        "factor": "0.000000000000001",
        "unit": "Q169893",
        "label": "femtosiemens",
        "siLabel": "siemens"
    },
    "Q95676279": {
        "factor": "0.000000000000000000000001",
        "unit": "Q169893",
        "label": "yoctosiemens",
        "siLabel": "siemens"
    },
    "Q95676287": {
        "factor": "100",
        "unit": "Q169893",
        "label": "hectosiemens",
        "siLabel": "siemens"
    },
    "Q95676291": {
        "factor": "10",
        "unit": "Q169893",
        "label": "decasiemens",
        "siLabel": "siemens"
    },
    "Q95676297": {
        "factor": "0.1",
        "unit": "Q169893",
        "label": "decisiemens",
        "siLabel": "siemens"
    },
    "Q95676298": {
        "factor": "1000000000000000000",
        "unit": "Q169893",
        "label": "exasiemens",
        "siLabel": "siemens"
    },
    "Q95689145": {
        "factor": "6378100",
        "unit": "Q11573",
        "label": "Earth radius",
        "siLabel": "metre"
    },
    "Q95720731": {
        "factor": "1000000000000000000000000",
        "unit": "Q190095",
        "label": "yottagray",
        "siLabel": "gray"
    },
    "Q95720734": {
        "factor": "1000000000000",
        "unit": "Q190095",
        "label": "teragray",
        "siLabel": "gray"
    },
    "Q95720736": {
        "factor": "0.000000000000001",
        "unit": "Q190095",
        "label": "femtogray",
        "siLabel": "gray"
    },
    "Q95720739": {
        "factor": "0.000000000000000000000001",
        "unit": "Q190095",
        "label": "yoctogray",
        "siLabel": "gray"
    },
    "Q95720741": {
        "factor": "0.000000000000000000001",
        "unit": "Q190095",
        "label": "zeptogray",
        "siLabel": "gray"
    },
    "Q95720742": {
        "factor": "1000000000000000000",
        "unit": "Q190095",
        "label": "exagray",
        "siLabel": "gray"
    },
    "Q95720746": {
        "factor": "100",
        "unit": "Q190095",
        "label": "hectogray",
        "siLabel": "gray"
    },
    "Q95720749": {
        "factor": "0.001",
        "unit": "Q179836",
        "label": "millilux",
        "siLabel": "lux"
    },
    "Q95720758": {
        "factor": "0.000001",
        "unit": "Q179836",
        "label": "microlux",
        "siLabel": "lux"
    },
    "Q95720773": {
        "factor": "10",
        "unit": "Q179836",
        "label": "decalux",
        "siLabel": "lux"
    },
    "Q95720777": {
        "factor": "100",
        "unit": "Q179836",
        "label": "hectolux",
        "siLabel": "lux"
    },
    "Q95720781": {
        "factor": "0.1",
        "unit": "Q179836",
        "label": "decilux",
        "siLabel": "lux"
    },
    "Q95720786": {
        "factor": "0.01",
        "unit": "Q179836",
        "label": "centilux",
        "siLabel": "lux"
    },
    "Q95857671": {
        "factor": "0.000000000000000000001",
        "unit": "Q103246",
        "label": "zeptosievert",
        "siLabel": "sievert"
    },
    "Q95859071": {
        "factor": "0.000000000000001",
        "unit": "Q103246",
        "label": "femtosievert",
        "siLabel": "sievert"
    },
    "Q95860960": {
        "factor": "10",
        "unit": "Q103246",
        "label": "decasievert",
        "siLabel": "sievert"
    },
    "Q95861107": {
        "factor": "100",
        "unit": "Q103246",
        "label": "hectosievert",
        "siLabel": "sievert"
    },
    "Q95861296": {
        "factor": "0.1",
        "unit": "Q103246",
        "label": "decisievert",
        "siLabel": "sievert"
    },
    "Q95862182": {
        "factor": "1000000000000000000",
        "unit": "Q103246",
        "label": "exasievert",
        "siLabel": "sievert"
    },
    "Q95863358": {
        "factor": "0.01",
        "unit": "Q103246",
        "label": "centisievert",
        "siLabel": "sievert"
    },
    "Q95863591": {
        "factor": "0.000000000000000000000001",
        "unit": "Q103246",
        "label": "yoctosievert",
        "siLabel": "sievert"
    },
    "Q95863894": {
        "factor": "0.000000000001",
        "unit": "Q103246",
        "label": "picosievert",
        "siLabel": "sievert"
    },
    "Q95864194": {
        "factor": "0.000000000000000000001",
        "unit": "Q102573",
        "label": "zeptobecquerel",
        "siLabel": "becquerel"
    },
    "Q95864378": {
        "factor": "0.000000000000001",
        "unit": "Q102573",
        "label": "femtobecquerel",
        "siLabel": "becquerel"
    },
    "Q95864695": {
        "factor": "10",
        "unit": "Q102573",
        "label": "decabecquerel",
        "siLabel": "becquerel"
    },
    "Q95864940": {
        "factor": "100",
        "unit": "Q102573",
        "label": "hectobecquerel",
        "siLabel": "becquerel"
    },
    "Q95865286": {
        "factor": "0.1",
        "unit": "Q102573",
        "label": "decibecquerel",
        "siLabel": "becquerel"
    },
    "Q95865530": {
        "factor": "1000000000000000000",
        "unit": "Q102573",
        "label": "exabecquerel",
        "siLabel": "becquerel"
    },
    "Q95865716": {
        "factor": "0.01",
        "unit": "Q102573",
        "label": "centibecquerel",
        "siLabel": "becquerel"
    },
    "Q95865877": {
        "factor": "0.000000000000000000000001",
        "unit": "Q102573",
        "label": "yoctobecquerel",
        "siLabel": "becquerel"
    },
    "Q95866173": {
        "factor": "0.000000000001",
        "unit": "Q102573",
        "label": "picobecquerel",
        "siLabel": "becquerel"
    },
    "Q95866344": {
        "factor": "0.000000001",
        "unit": "Q102573",
        "label": "nanobecquerel",
        "siLabel": "becquerel"
    },
    "Q95866767": {
        "factor": "0.001",
        "unit": "Q102573",
        "label": "millibecquerel",
        "siLabel": "becquerel"
    },
    "Q95867993": {
        "factor": "0.001",
        "unit": "Q12438",
        "label": "millinewton",
        "siLabel": "newton"
    },
    "Q95948345": {
        "factor": "0.01",
        "unit": "Q33680",
        "label": "centiradian",
        "siLabel": "radian"
    },
    "Q95948364": {
        "factor": "0.1",
        "unit": "Q33680",
        "label": "deciradian",
        "siLabel": "radian"
    },
    "Q95948628": {
        "factor": "0.000981748",
        "unit": "Q33680",
        "label": "angular mil",
        "siLabel": "radian"
    },
    "Q95948734": {
        "factor": "10",
        "unit": "Q12438",
        "label": "decanewton",
        "siLabel": "newton"
    },
    "Q95948739": {
        "factor": "100",
        "unit": "Q12438",
        "label": "hectonewton",
        "siLabel": "newton"
    },
    "Q95948747": {
        "factor": "0.1",
        "unit": "Q12438",
        "label": "decinewton",
        "siLabel": "newton"
    },
    "Q95976839": {
        "factor": "1000000000000000",
        "unit": "Q484092",
        "label": "petalumen",
        "siLabel": "lumen"
    },
    "Q95976853": {
        "factor": "1000000000",
        "unit": "Q484092",
        "label": "gigalumen",
        "siLabel": "lumen"
    },
    "Q95976869": {
        "factor": "1000000000000000000000000",
        "unit": "Q484092",
        "label": "yottalumen",
        "siLabel": "lumen"
    },
    "Q95976889": {
        "factor": "0.000000000000000000000001",
        "unit": "Q484092",
        "label": "yoctolumen",
        "siLabel": "lumen"
    },
    "Q95976917": {
        "factor": "0.1",
        "unit": "Q484092",
        "label": "decilumen",
        "siLabel": "lumen"
    },
    "Q95976919": {
        "factor": "1000000000000000000",
        "unit": "Q484092",
        "label": "exalumen",
        "siLabel": "lumen"
    },
    "Q95976921": {
        "factor": "0.000000001",
        "unit": "Q163343",
        "label": "nanotesla",
        "siLabel": "tesla"
    },
    "Q95993516": {
        "factor": "1000000000000",
        "unit": "Q12438",
        "label": "teranewton",
        "siLabel": "newton"
    },
    "Q95993522": {
        "factor": "0.000000001",
        "unit": "Q12438",
        "label": "nanonewton",
        "siLabel": "newton"
    },
    "Q95993524": {
        "factor": "0.000000000000001",
        "unit": "Q12438",
        "label": "femtonewton",
        "siLabel": "newton"
    },
    "Q95993526": {
        "factor": "0.000000000000000000000001",
        "unit": "Q12438",
        "label": "yoctonewton",
        "siLabel": "newton"
    },
    "Q95993528": {
        "factor": "0.000000000000000000001",
        "unit": "Q12438",
        "label": "zeptonewton",
        "siLabel": "newton"
    },
    "Q95993530": {
        "factor": "1000000000000000000",
        "unit": "Q12438",
        "label": "exanewton",
        "siLabel": "newton"
    },
    "Q95993532": {
        "factor": "0.000000000001",
        "unit": "Q12438",
        "label": "piconewton",
        "siLabel": "newton"
    },
    "Q95993537": {
        "factor": "0.000001",
        "unit": "Q33680",
        "label": "microradian",
        "siLabel": "radian"
    },
    "Q95993542": {
        "factor": "0.000000001",
        "unit": "Q33680",
        "label": "nanoradian",
        "siLabel": "radian"
    },
    "Q95993547": {
        "factor": "0.000000000000001",
        "unit": "Q33680",
        "label": "femtoradian",
        "siLabel": "radian"
    },
    "Q95993553": {
        "factor": "0.000000000001",
        "unit": "Q33680",
        "label": "picoradian",
        "siLabel": "radian"
    },
    "Q95993554": {
        "factor": "10",
        "unit": "Q33680",
        "label": "decaradian",
        "siLabel": "radian"
    },
    "Q95993557": {
        "factor": "100",
        "unit": "Q33680",
        "label": "hectoradian",
        "siLabel": "radian"
    },
    "Q95993619": {
        "factor": "0.000000000001",
        "unit": "Q163343",
        "label": "picotesla",
        "siLabel": "tesla"
    },
    "Q96025401": {
        "factor": "10",
        "unit": "Q163343",
        "label": "decatesla",
        "siLabel": "tesla"
    },
    "Q96025405": {
        "factor": "1000000000000",
        "unit": "Q33680",
        "label": "teraradian",
        "siLabel": "radian"
    },
    "Q96025407": {
        "factor": "1000000000000000000000",
        "unit": "Q33680",
        "label": "zettaradian",
        "siLabel": "radian"
    },
    "Q96025409": {
        "factor": "0.000000000000000000001",
        "unit": "Q33680",
        "label": "zeptoradian",
        "siLabel": "radian"
    },
    "Q96025413": {
        "factor": "0.000000000000000000000001",
        "unit": "Q33680",
        "label": "yoctoradian",
        "siLabel": "radian"
    },
    "Q96025414": {
        "factor": "1000000000000000000",
        "unit": "Q33680",
        "label": "exaradian",
        "siLabel": "radian"
    },
    "Q96025419": {
        "factor": "1000000000000000000000000",
        "unit": "Q179836",
        "label": "yottalux",
        "siLabel": "lux"
    },
    "Q96025422": {
        "factor": "1000000000",
        "unit": "Q179836",
        "label": "gigalux",
        "siLabel": "lux"
    },
    "Q96025427": {
        "factor": "1000000000000000",
        "unit": "Q179836",
        "label": "petalux",
        "siLabel": "lux"
    },
    "Q96025431": {
        "factor": "1000000",
        "unit": "Q179836",
        "label": "megalux",
        "siLabel": "lux"
    },
    "Q96025433": {
        "factor": "1000000000000",
        "unit": "Q179836",
        "label": "teralux",
        "siLabel": "lux"
    },
    "Q96025435": {
        "factor": "0.000000001",
        "unit": "Q179836",
        "label": "nanolux",
        "siLabel": "lux"
    },
    "Q96025441": {
        "factor": "0.000000000000001",
        "unit": "Q179836",
        "label": "femtolux",
        "siLabel": "lux"
    },
    "Q96050953": {
        "factor": "1000000000",
        "unit": "Q163354",
        "label": "gigahenry",
        "siLabel": "henry"
    },
    "Q96051010": {
        "factor": "1000000000000000",
        "unit": "Q163354",
        "label": "petahenry",
        "siLabel": "henry"
    },
    "Q96051029": {
        "factor": "1000000000000000000000000",
        "unit": "Q163354",
        "label": "yottahenry",
        "siLabel": "henry"
    },
    "Q96051052": {
        "factor": "0.01",
        "unit": "Q163354",
        "label": "centihenry",
        "siLabel": "henry"
    },
    "Q96051074": {
        "factor": "1000000000000",
        "unit": "Q163354",
        "label": "terahenry",
        "siLabel": "henry"
    },
    "Q96051106": {
        "factor": "1000000",
        "unit": "Q163354",
        "label": "megahenry",
        "siLabel": "henry"
    },
    "Q96051123": {
        "factor": "1000",
        "unit": "Q163354",
        "label": "kilohenry",
        "siLabel": "henry"
    },
    "Q96051126": {
        "factor": "0.000000000000001",
        "unit": "Q163354",
        "label": "femtohenry",
        "siLabel": "henry"
    },
    "Q96051133": {
        "factor": "0.000000000000000000000001",
        "unit": "Q163354",
        "label": "yoctohenry",
        "siLabel": "henry"
    },
    "Q96051139": {
        "factor": "100",
        "unit": "Q163354",
        "label": "hectohenry",
        "siLabel": "henry"
    },
    "Q96051142": {
        "factor": "0.1",
        "unit": "Q163354",
        "label": "decihenry",
        "siLabel": "henry"
    },
    "Q96051144": {
        "factor": "1000000000000000000",
        "unit": "Q163354",
        "label": "exahenry",
        "siLabel": "henry"
    },
    "Q96051150": {
        "factor": "0.000000000001",
        "unit": "Q163354",
        "label": "picohenry",
        "siLabel": "henry"
    },
    "Q96051160": {
        "factor": "10",
        "unit": "Q163354",
        "label": "decahenry",
        "siLabel": "henry"
    },
    "Q96051186": {
        "factor": "0.000000000000000000001",
        "unit": "Q163354",
        "label": "zeptohenry",
        "siLabel": "henry"
    },
    "Q96051199": {
        "factor": "0.000000000000000001",
        "unit": "Q163354",
        "label": "attohenry",
        "siLabel": "henry"
    },
    "Q96051245": {
        "factor": "0.000000000000000000000001",
        "unit": "Q179836",
        "label": "yoctolux",
        "siLabel": "lux"
    },
    "Q96051267": {
        "factor": "1000000000000000000",
        "unit": "Q179836",
        "label": "exalux",
        "siLabel": "lux"
    },
    "Q96051282": {
        "factor": "0.000000000001",
        "unit": "Q179836",
        "label": "picolux",
        "siLabel": "lux"
    },
    "Q96051312": {
        "factor": "0.000000000000000000001",
        "unit": "Q179836",
        "label": "zeptolux",
        "siLabel": "lux"
    },
    "Q96070067": {
        "factor": "1000000000000000",
        "unit": "Q163343",
        "label": "petatesla",
        "siLabel": "tesla"
    },
    "Q96070074": {
        "factor": "1000000000000000000000000",
        "unit": "Q163343",
        "label": "yottatesla",
        "siLabel": "tesla"
    },
    "Q96070076": {
        "factor": "1000000000",
        "unit": "Q163343",
        "label": "gigatesla",
        "siLabel": "tesla"
    },
    "Q96070087": {
        "factor": "0.01",
        "unit": "Q163343",
        "label": "centitesla",
        "siLabel": "tesla"
    },
    "Q96070103": {
        "factor": "1000000",
        "unit": "Q163343",
        "label": "megatesla",
        "siLabel": "tesla"
    },
    "Q96070125": {
        "factor": "100",
        "unit": "Q163343",
        "label": "hectotesla",
        "siLabel": "tesla"
    },
    "Q96070145": {
        "factor": "0.000000000000001",
        "unit": "Q163343",
        "label": "femtotesla",
        "siLabel": "tesla"
    },
    "Q96070174": {
        "factor": "1000000000000",
        "unit": "Q163343",
        "label": "teratesla",
        "siLabel": "tesla"
    },
    "Q96070195": {
        "factor": "0.000000000000000000001",
        "unit": "Q163343",
        "label": "zeptotesla",
        "siLabel": "tesla"
    },
    "Q96070247": {
        "factor": "0.000000000000000000000001",
        "unit": "Q163343",
        "label": "yoctotesla",
        "siLabel": "tesla"
    },
    "Q96070254": {
        "factor": "0.1",
        "unit": "Q163343",
        "label": "decitesla",
        "siLabel": "tesla"
    },
    "Q96070264": {
        "factor": "1000000000000000000",
        "unit": "Q163343",
        "label": "exatesla",
        "siLabel": "tesla"
    },
    "Q96070318": {
        "factor": "0.1",
        "unit": "Q177612",
        "label": "decisteradian",
        "siLabel": "steradian"
    },
    "Q96070329": {
        "factor": "0.000000001",
        "unit": "Q177612",
        "label": "nanosteradian",
        "siLabel": "steradian"
    },
    "Q96070341": {
        "factor": "0.000000000001",
        "unit": "Q177612",
        "label": "picosteradian",
        "siLabel": "steradian"
    },
    "Q96095866": {
        "factor": "0.000000000000001",
        "unit": "Q177612",
        "label": "femtosteradian",
        "siLabel": "steradian"
    },
    "Q96095897": {
        "factor": "0.000000000000000000001",
        "unit": "Q177612",
        "label": "zeptosteradian",
        "siLabel": "steradian"
    },
    "Q96095917": {
        "factor": "0.000000000000000000000001",
        "unit": "Q177612",
        "label": "yoctosteradian",
        "siLabel": "steradian"
    },
    "Q96095927": {
        "factor": "10",
        "unit": "Q177612",
        "label": "decasteradian",
        "siLabel": "steradian"
    },
    "Q96095928": {
        "factor": "100",
        "unit": "Q177612",
        "label": "hectosteradian",
        "siLabel": "steradian"
    },
    "Q96095931": {
        "factor": "1000",
        "unit": "Q177612",
        "label": "kilosteradian",
        "siLabel": "steradian"
    },
    "Q96095933": {
        "factor": "1000000",
        "unit": "Q177612",
        "label": "megasteradian",
        "siLabel": "steradian"
    },
    "Q96095939": {
        "factor": "1000000000",
        "unit": "Q177612",
        "label": "gigasteradian",
        "siLabel": "steradian"
    },
    "Q96106290": {
        "factor": "1000000000000",
        "unit": "Q177612",
        "label": "terasteradian",
        "siLabel": "steradian"
    },
    "Q96106298": {
        "factor": "1000000000000000",
        "unit": "Q177612",
        "label": "petasteradian",
        "siLabel": "steradian"
    },
    "Q96106311": {
        "factor": "1000000000000000000",
        "unit": "Q177612",
        "label": "exasteradian",
        "siLabel": "steradian"
    },
    "Q96106319": {
        "factor": "1000000000000000000000",
        "unit": "Q177612",
        "label": "zettasteradian",
        "siLabel": "steradian"
    },
    "Q96106332": {
        "factor": "1000000000000000000000000",
        "unit": "Q177612",
        "label": "yottasteradian",
        "siLabel": "steradian"
    },
    "Q96192470": {
        "factor": "1",
        "unit": "Q96192470",
        "label": "watt per metre",
        "siLabel": "watt per metre"
    },
    "Q96309077": {
        "factor": "1",
        "unit": "Q96309077",
        "label": "siemens square metre per mole",
        "siLabel": "siemens square metre per mole"
    },
    "Q96312779": {
        "factor": "0.000000000004848136811095356",
        "unit": "Q33680",
        "label": "microarcsecond",
        "siLabel": "radian"
    },
    "Q96347486": {
        "factor": "1",
        "unit": "Q96347486",
        "label": "radian square metre per mole",
        "siLabel": "radian square metre per mole"
    },
    "Q96347983": {
        "factor": "1",
        "unit": "Q96347983",
        "label": "radian square metre per kilogram",
        "siLabel": "radian square metre per kilogram"
    },
    "Q96760033": {
        "factor": "62760000000000",
        "unit": "Q25269",
        "label": "Hiroshima-equivalent",
        "siLabel": "joule"
    },
    "Q97496530": {
        "factor": "0.0000000000000000001602176634",
        "unit": "Q1709783",
        "label": "electronvolt second",
        "siLabel": "joule second"
    },
    "Q97540991": {
        "factor": "1",
        "unit": "Q97540991",
        "label": "ampere square metre per joule second",
        "siLabel": "ampere square metre per joule second"
    },
    "Q97541209": {
        "factor": "1",
        "unit": "Q97541209",
        "label": "ampere second per kilogram",
        "siLabel": "ampere second per kilogram"
    },
    "Q97543281": {
        "factor": "1",
        "unit": "Q97543281",
        "label": "per tesla second",
        "siLabel": "per tesla second"
    },
    "Q98102832": {
        "factor": "1",
        "unit": "Q98102832",
        "label": "becquerel per cubic metre",
        "siLabel": "becquerel per cubic metre"
    },
    "Q98103135": {
        "factor": "1",
        "unit": "Q98103135",
        "label": "becquerel per square metre",
        "siLabel": "becquerel per square metre"
    },
    "Q98266832": {
        "factor": "1",
        "unit": "Q98266832",
        "label": "square metre per steradian",
        "siLabel": "square metre per steradian"
    },
    "Q98267267": {
        "factor": "1",
        "unit": "Q98267267",
        "label": "square metre per joule",
        "siLabel": "square metre per joule"
    },
    "Q98269780": {
        "factor": "1",
        "unit": "Q98269780",
        "label": "square metre per steradian joule",
        "siLabel": "square metre per steradian joule"
    },
    "Q98391507": {
        "factor": "4184000000",
        "unit": "Q25269",
        "label": "ton of TNT",
        "siLabel": "joule"
    },
    "Q98492214": {
        "factor": "0.0000001111",
        "unit": "Q25999243",
        "label": "denier",
        "siLabel": "kilogram per metre"
    },
    "Q98538634": {
        "factor": "0.000000000000000000160218",
        "unit": "Q80374519",
        "label": "electronvolt per square metre",
        "siLabel": "joule per square metre"
    },
    "Q98635536": {
        "factor": "0.000000000000000000160218",
        "unit": "Q56023789",
        "label": "electronvolt per metre",
        "siLabel": "joule per metre"
    },
    "Q98642859": {
        "factor": "0.000000000000000000160218",
        "unit": "Q98643033",
        "label": "electronvolt square metre per kilogram",
        "siLabel": "joule square metre per kilogram"
    },
    "Q98643033": {
        "factor": "1",
        "unit": "Q98643033",
        "label": "joule square metre per kilogram",
        "siLabel": "joule square metre per kilogram"
    },
    "Q98793302": {
        "factor": "0.0011365225",
        "unit": "Q25517",
        "label": "quart (UK)",
        "siLabel": "cubic metre"
    },
    "Q98793408": {
        "factor": "0.0009463529",
        "unit": "Q25517",
        "label": "liquid quart (US)",
        "siLabel": "cubic metre"
    },
    "Q98793687": {
        "factor": "0.001101221",
        "unit": "Q25517",
        "label": "dry quart (US)",
        "siLabel": "cubic metre"
    },
    "Q98813401": {
        "factor": "1",
        "unit": "Q98813401",
        "label": "square metre per volt second",
        "siLabel": "square metre per volt second"
    },
    "Q98915792": {
        "factor": "1",
        "unit": "Q98915792",
        "label": "per cubic metre second",
        "siLabel": "per cubic metre second"
    },
    "Q99228736": {
        "factor": "0.3",
        "unit": "Q11573",
        "label": "Q99228736",
        "siLabel": "metre"
    },
    "Q99228747": {
        "factor": "2.1",
        "unit": "Q11573",
        "label": "Q99228747",
        "siLabel": "metre"
    },
    "Q99476928": {
        "factor": "0.00980665",
        "unit": "Q12438",
        "label": "gram-force",
        "siLabel": "newton"
    },
    "Q99487704": {
        "factor": "0.001",
        "unit": "Q199",
        "label": "parts per thousand",
        "siLabel": "1"
    },
    "Q99488743": {
        "factor": "4.1855",
        "unit": "Q25269",
        "label": "calorie (15 \u00b0C)",
        "siLabel": "joule"
    },
    "Q99488951": {
        "factor": "4.182",
        "unit": "Q25269",
        "label": "calorie (20 \u00b0C)",
        "siLabel": "joule"
    },
    "Q99489408": {
        "factor": "4.204",
        "unit": "Q25269",
        "label": "calorie (4 \u00b0C)",
        "siLabel": "joule"
    },
    "Q99490009": {
        "factor": "1055.05585",
        "unit": "Q25269",
        "label": "British thermal unit (IT)",
        "siLabel": "joule"
    },
    "Q99490301": {
        "factor": "1055.06",
        "unit": "Q25269",
        "label": "British thermal unit (ISO)",
        "siLabel": "joule"
    },
    "Q99490479": {
        "factor": "1059.67",
        "unit": "Q25269",
        "label": "British thermal unit (39 \u00b0F)",
        "siLabel": "joule"
    },
    "Q99490986": {
        "factor": "1054.8",
        "unit": "Q25269",
        "label": "British thermal unit (59 \u00b0F)",
        "siLabel": "joule"
    },
    "Q99491193": {
        "factor": "1054.68",
        "unit": "Q25269",
        "label": "British thermal unit (60 \u00b0F)",
        "siLabel": "joule"
    },
    "Q99491447": {
        "factor": "1055.87",
        "unit": "Q25269",
        "label": "British thermal unit (mean)",
        "siLabel": "joule"
    },
    "Q99492167": {
        "factor": "133322",
        "unit": "Q44395",
        "label": "metre of mercury",
        "siLabel": "pascal"
    },
    "Q99605059": {
        "factor": "1",
        "unit": "Q99605059",
        "label": "sievert per second",
        "siLabel": "sievert per second"
    },
    "Q99721917": {
        "factor": "1",
        "unit": "Q99721917",
        "label": "coulomb per kilogram second",
        "siLabel": "coulomb per kilogram second"
    },
    "Q100036106": {
        "factor": "1852",
        "unit": "Q11573",
        "label": "international nautical mile",
        "siLabel": "metre"
    },
    "Q100039658": {
        "factor": "0.0000254",
        "unit": "Q11573",
        "label": "international mil",
        "siLabel": "metre"
    },
    "Q100046246": {
        "factor": "0.0254",
        "unit": "Q11573",
        "label": "inch (US survey)",
        "siLabel": "metre"
    },
    "Q100051890": {
        "factor": "1.828803658",
        "unit": "Q11573",
        "label": "fathom (US survey)",
        "siLabel": "metre"
    },
    "Q100054009": {
        "factor": "201.1684023",
        "unit": "Q11573",
        "label": "US survey furlong",
        "siLabel": "metre"
    },
    "Q100055982": {
        "factor": "4046.87261",
        "unit": "Q25343",
        "label": "US survey acre",
        "siLabel": "square metre"
    },
    "Q100059432": {
        "factor": "93239571.97",
        "unit": "Q25343",
        "label": "township",
        "siLabel": "square metre"
    },
    "Q100060248": {
        "factor": "0.0000254000508",
        "unit": "Q11573",
        "label": "US survey mil",
        "siLabel": "metre"
    },
    "Q100063122": {
        "factor": "0.02539998",
        "unit": "Q11573",
        "label": "British Imperial inch",
        "siLabel": "metre"
    },
    "Q100064794": {
        "factor": "0.3047997",
        "unit": "Q11573",
        "label": "British Imperial foot",
        "siLabel": "metre"
    },
    "Q100158369": {
        "factor": "5.0292",
        "unit": "Q11573",
        "label": "British Imperial rod",
        "siLabel": "metre"
    },
    "Q100158510": {
        "factor": "1.8288",
        "unit": "Q11573",
        "label": "British Imperial fathom",
        "siLabel": "metre"
    },
    "Q100158590": {
        "factor": "0.914399",
        "unit": "Q11573",
        "label": "British Imperial yard",
        "siLabel": "metre"
    },
    "Q100158595": {
        "factor": "1609.34",
        "unit": "Q11573",
        "label": "British Imperial mile",
        "siLabel": "metre"
    },
    "Q100158603": {
        "factor": "1853.18",
        "unit": "Q11573",
        "label": "British Imperial nautical mile",
        "siLabel": "metre"
    },
    "Q100257348": {
        "factor": "105506000",
        "unit": "Q25269",
        "label": "therm (EC)",
        "siLabel": "joule"
    },
    "Q100293463": {
        "factor": "1",
        "unit": "Q100293463",
        "label": "reciprocal pascal second",
        "siLabel": "reciprocal pascal second"
    },
    "Q100293891": {
        "factor": "1",
        "unit": "Q100293891",
        "label": "volt second",
        "siLabel": "volt second"
    },
    "Q100294053": {
        "factor": "1",
        "unit": "Q100294053",
        "label": "watt per steradian metre",
        "siLabel": "watt per steradian metre"
    },
    "Q100296845": {
        "factor": "1",
        "unit": "Q2844478",
        "label": "lenz",
        "siLabel": "ampere per metre"
    },
    "Q100335456": {
        "factor": "30.48",
        "unit": "Q11573",
        "label": "Ramsden chain",
        "siLabel": "metre"
    },
    "Q100371665": {
        "factor": "20.117",
        "unit": "Q11573",
        "label": "Gunter's chain (UK)",
        "siLabel": "metre"
    },
    "Q100989321": {
        "factor": "1",
        "unit": "Q910311",
        "label": "talbot",
        "siLabel": "lumen second"
    },
    "Q101194838": {
        "factor": "1000000000",
        "unit": "Q101195156",
        "label": "gigahertz per volt",
        "siLabel": "hertz per volt"
    },
    "Q101195156": {
        "factor": "1",
        "unit": "Q101195156",
        "label": "hertz per volt",
        "siLabel": "hertz per volt"
    },
    "Q101427291": {
        "factor": "0.3732417",
        "unit": "Q11570",
        "label": "apothecaries' pound",
        "siLabel": "kilogram"
    },
    "Q101427557": {
        "factor": "0.0000000003335641",
        "unit": "Q25406",
        "label": "franklin",
        "siLabel": "coulomb"
    },
    "Q101427873": {
        "factor": "0.008809768",
        "unit": "Q25517",
        "label": "peck (US)",
        "siLabel": "cubic metre"
    },
    "Q101427917": {
        "factor": "0.00909218",
        "unit": "Q25517",
        "label": "peck (UK)",
        "siLabel": "cubic metre"
    },
    "Q101428098": {
        "factor": "10000",
        "unit": "Q44395",
        "label": "decibar",
        "siLabel": "pascal"
    },
    "Q101428103": {
        "factor": "0.1",
        "unit": "Q44395",
        "label": "microbar",
        "siLabel": "pascal"
    },
    "Q101434890": {
        "factor": "1",
        "unit": "Q101434890",
        "label": "watt per steradian square metre hertz",
        "siLabel": "watt per steradian square metre hertz"
    },
    "Q101435195": {
        "factor": "1",
        "unit": "Q101435195",
        "label": "joule per square metre hertz",
        "siLabel": "joule per square metre hertz"
    },
    "Q101435213": {
        "factor": "0.00000000000000000000000001",
        "unit": "Q101435195",
        "label": "jansky second",
        "siLabel": "joule per square metre hertz"
    },
    "Q101435269": {
        "factor": "3590.17",
        "unit": "Q11574",
        "label": "sidereal hour",
        "siLabel": "second"
    },
    "Q101435276": {
        "factor": "59.83617",
        "unit": "Q11574",
        "label": "sidereal minute",
        "siLabel": "second"
    },
    "Q101435282": {
        "factor": "0.9972696",
        "unit": "Q11574",
        "label": "sidereal second",
        "siLabel": "second"
    },
    "Q101435332": {
        "factor": "1333.22",
        "unit": "Q44395",
        "label": "centimetre of mercury",
        "siLabel": "pascal"
    },
    "Q101435403": {
        "factor": "4190",
        "unit": "Q25269",
        "label": "kilocalorie (mean)",
        "siLabel": "joule"
    },
    "Q101435408": {
        "factor": "0.1",
        "unit": "Q25269",
        "label": "megaerg",
        "siLabel": "joule"
    },
    "Q101460091": {
        "factor": "1",
        "unit": "Q101460091",
        "label": "joule per cubic metre hertz",
        "siLabel": "joule per cubic metre hertz"
    },
    "Q101460900": {
        "factor": "1",
        "unit": "Q101460900",
        "label": "watt per hertz",
        "siLabel": "watt per hertz"
    },
    "Q101461942": {
        "factor": "1",
        "unit": "Q101461942",
        "label": "watt per steradian hertz",
        "siLabel": "watt per steradian hertz"
    },
    "Q101463141": {
        "factor": "0.000000000000000000000000000000000000000000000001",
        "unit": "Q25343",
        "label": "square yoctometre",
        "siLabel": "square metre"
    },
    "Q101463237": {
        "factor": "0.000000000000000000000000000000000000000001",
        "unit": "Q25343",
        "label": "square zeptometre",
        "siLabel": "square metre"
    },
    "Q101463321": {
        "factor": "0.000000000000000000000000000000000001",
        "unit": "Q25343",
        "label": "square attometre",
        "siLabel": "square metre"
    },
    "Q101463409": {
        "factor": "0.000000000000000000000000000001",
        "unit": "Q25343",
        "label": "square femtometre",
        "siLabel": "square metre"
    },
    "Q101463496": {
        "factor": "0.000000000000000000000001",
        "unit": "Q25343",
        "label": "square picometre",
        "siLabel": "square metre"
    },
    "Q101463679": {
        "factor": "10000",
        "unit": "Q25343",
        "label": "square hectometre",
        "siLabel": "square metre"
    },
    "Q101464050": {
        "factor": "1000000000000",
        "unit": "Q25343",
        "label": "square megametre",
        "siLabel": "square metre"
    },
    "Q101464215": {
        "factor": "1000000000000000000",
        "unit": "Q25343",
        "label": "square gigametre",
        "siLabel": "square metre"
    },
    "Q101464369": {
        "factor": "1000000000000000000000000",
        "unit": "Q25343",
        "label": "square terametre",
        "siLabel": "square metre"
    },
    "Q101464499": {
        "factor": "1000000000000000000000000000000",
        "unit": "Q25343",
        "label": "square petametre",
        "siLabel": "square metre"
    },
    "Q101464624": {
        "factor": "1000000000000000000000000000000000000",
        "unit": "Q25343",
        "label": "square exametre",
        "siLabel": "square metre"
    },
    "Q101464753": {
        "factor": "1000000000000000000000000000000000000000000",
        "unit": "Q25343",
        "label": "square zettametre",
        "siLabel": "square metre"
    },
    "Q101464875": {
        "factor": "1000000000000000000000000000000000000000000000000",
        "unit": "Q25343",
        "label": "square yottametre",
        "siLabel": "square metre"
    },
    "Q101514563": {
        "factor": "0.00177185",
        "unit": "Q11570",
        "label": "dram (avoirdupois)",
        "siLabel": "kilogram"
    },
    "Q101515060": {
        "factor": "0.001",
        "unit": "Q101515303",
        "label": "gram per joule",
        "siLabel": "kilogram per joule"
    },
    "Q101515303": {
        "factor": "1",
        "unit": "Q101515303",
        "label": "kilogram per joule",
        "siLabel": "kilogram per joule"
    },
    "Q101875087": {
        "factor": "10000",
        "unit": "Q281096",
        "label": "candela per square centimetre",
        "siLabel": "candela per square metre"
    },
    "Q101877596": {
        "factor": "1000",
        "unit": "Q844211",
        "label": "gram per millilitre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q101879174": {
        "factor": "0.1",
        "unit": "Q182429",
        "label": "decimetre per second",
        "siLabel": "metre per second"
    },
    "Q101881680": {
        "factor": "3.306",
        "unit": "Q25343",
        "label": "tsubo",
        "siLabel": "square metre"
    },
    "Q102068844": {
        "factor": "1000000",
        "unit": "Q21401573",
        "label": "reciprocal cubic centimetre",
        "siLabel": "reciprocal cubic metre"
    },
    "Q102129339": {
        "factor": "0.0166667",
        "unit": "Q6137407",
        "label": "reciprocal minute",
        "siLabel": "reciprocal second"
    },
    "Q102129428": {
        "factor": "0.000277778",
        "unit": "Q6137407",
        "label": "reciprocal hour",
        "siLabel": "reciprocal second"
    },
    "Q102129592": {
        "factor": "0.0000115741",
        "unit": "Q6137407",
        "label": "reciprocal day",
        "siLabel": "reciprocal second"
    },
    "Q102129764": {
        "factor": "0.0000000317098",
        "unit": "Q6137407",
        "label": "reciprocal year",
        "siLabel": "reciprocal second"
    },
    "Q102130673": {
        "factor": "0.000000000000000000000001",
        "unit": "Q182429",
        "label": "yoctometre per second",
        "siLabel": "metre per second"
    },
    "Q102130674": {
        "factor": "0.000000000000000000001",
        "unit": "Q182429",
        "label": "zeptometre per second",
        "siLabel": "metre per second"
    },
    "Q102130677": {
        "factor": "0.000000000000000001",
        "unit": "Q182429",
        "label": "attometre per second",
        "siLabel": "metre per second"
    },
    "Q102130679": {
        "factor": "0.000000000000001",
        "unit": "Q182429",
        "label": "femtometre per second",
        "siLabel": "metre per second"
    },
    "Q102130681": {
        "factor": "0.000000000001",
        "unit": "Q182429",
        "label": "picometre per second",
        "siLabel": "metre per second"
    },
    "Q102130684": {
        "factor": "0.000000001",
        "unit": "Q182429",
        "label": "nanometre per second",
        "siLabel": "metre per second"
    },
    "Q102130686": {
        "factor": "0.000001",
        "unit": "Q182429",
        "label": "micrometre per second",
        "siLabel": "metre per second"
    },
    "Q102130688": {
        "factor": "0.001",
        "unit": "Q182429",
        "label": "millimetre per second",
        "siLabel": "metre per second"
    },
    "Q102130690": {
        "factor": "10",
        "unit": "Q182429",
        "label": "decametre per second",
        "siLabel": "metre per second"
    },
    "Q102130692": {
        "factor": "100",
        "unit": "Q182429",
        "label": "hectometre per second",
        "siLabel": "metre per second"
    },
    "Q102130694": {
        "factor": "1000000",
        "unit": "Q182429",
        "label": "megametre per second",
        "siLabel": "metre per second"
    },
    "Q102130696": {
        "factor": "1000000000",
        "unit": "Q182429",
        "label": "gigametre per second",
        "siLabel": "metre per second"
    },
    "Q102130698": {
        "factor": "1000000000000",
        "unit": "Q182429",
        "label": "terametre per second",
        "siLabel": "metre per second"
    },
    "Q102130700": {
        "factor": "1000000000000000",
        "unit": "Q182429",
        "label": "petametre per second",
        "siLabel": "metre per second"
    },
    "Q102130702": {
        "factor": "1000000000000000000",
        "unit": "Q182429",
        "label": "exametre per second",
        "siLabel": "metre per second"
    },
    "Q102130704": {
        "factor": "1000000000000000000000",
        "unit": "Q182429",
        "label": "zettametre per second",
        "siLabel": "metre per second"
    },
    "Q102130706": {
        "factor": "1000000000000000000000000",
        "unit": "Q182429",
        "label": "yottametre per second",
        "siLabel": "metre per second"
    },
    "Q102130743": {
        "factor": "0.000000000000000000000001",
        "unit": "Q1051665",
        "label": "yoctometre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130745": {
        "factor": "0.000000000000000000001",
        "unit": "Q1051665",
        "label": "zeptometre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130747": {
        "factor": "0.000000000000000001",
        "unit": "Q1051665",
        "label": "attometre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130748": {
        "factor": "0.000000000000001",
        "unit": "Q1051665",
        "label": "femtometre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130751": {
        "factor": "0.000000000001",
        "unit": "Q1051665",
        "label": "picometre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130753": {
        "factor": "0.000000001",
        "unit": "Q1051665",
        "label": "nanometre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130755": {
        "factor": "0.000001",
        "unit": "Q1051665",
        "label": "micrometre per second squared",
        "siLabel": "metre per square second"
    },
    "Q102130756": {
        "factor": "0.001",
        "unit": "Q1051665",
        "label": "millimetre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130758": {
        "factor": "0.1",
        "unit": "Q1051665",
        "label": "decimetre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130759": {
        "factor": "10",
        "unit": "Q1051665",
        "label": "decametre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130761": {
        "factor": "100",
        "unit": "Q1051665",
        "label": "hectometre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130762": {
        "factor": "1000",
        "unit": "Q1051665",
        "label": "kilometre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130765": {
        "factor": "1000000",
        "unit": "Q1051665",
        "label": "megametre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130767": {
        "factor": "1000000000",
        "unit": "Q1051665",
        "label": "gigametre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130769": {
        "factor": "1000000000000",
        "unit": "Q1051665",
        "label": "terametre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130771": {
        "factor": "1000000000000000",
        "unit": "Q1051665",
        "label": "petametre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130773": {
        "factor": "1000000000000000000",
        "unit": "Q1051665",
        "label": "exametre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130775": {
        "factor": "1000000000000000000000",
        "unit": "Q1051665",
        "label": "zettametre per square second",
        "siLabel": "metre per square second"
    },
    "Q102130777": {
        "factor": "1000000000000000000000000",
        "unit": "Q1051665",
        "label": "yottametre per square second",
        "siLabel": "metre per square second"
    },
    "Q102178883": {
        "factor": "0.000000277778",
        "unit": "Q794261",
        "label": "cubic decimetre per hour",
        "siLabel": "cubic metre per second"
    },
    "Q103419450": {
        "factor": "1",
        "unit": "Q103419450",
        "label": "newton per cubic metre",
        "siLabel": "newton per cubic metre"
    },
    "Q104117265": {
        "factor": "10",
        "unit": "Q25272",
        "label": "biot",
        "siLabel": "ampere"
    },
    "Q104381302": {
        "factor": "1",
        "unit": "Q104381302",
        "label": "watt per cubic metre",
        "siLabel": "watt per cubic metre"
    },
    "Q104628312": {
        "factor": "1",
        "unit": "Q104628312",
        "label": "volt-ampere-reactive second",
        "siLabel": "volt-ampere-reactive second"
    },
    "Q104628670": {
        "factor": "0.000000115741",
        "unit": "Q182429",
        "label": "centimetre per day",
        "siLabel": "metre per second"
    },
    "Q104628684": {
        "factor": "0.0000115741",
        "unit": "Q182429",
        "label": "metre per day",
        "siLabel": "metre per second"
    },
    "Q104628868": {
        "factor": "1000000000000000000000000",
        "unit": "Q182429",
        "label": "metre per yoctosecond",
        "siLabel": "metre per second"
    },
    "Q104628869": {
        "factor": "1000000000000000000000",
        "unit": "Q182429",
        "label": "metre per zeptosecond",
        "siLabel": "metre per second"
    },
    "Q104628871": {
        "factor": "1000000000000000000",
        "unit": "Q182429",
        "label": "metre per attosecond",
        "siLabel": "metre per second"
    },
    "Q104628872": {
        "factor": "1000000000000000",
        "unit": "Q182429",
        "label": "metre per femtosecond",
        "siLabel": "metre per second"
    },
    "Q104628873": {
        "factor": "1000000000000",
        "unit": "Q182429",
        "label": "metre per picosecond",
        "siLabel": "metre per second"
    },
    "Q104628874": {
        "factor": "1000000000",
        "unit": "Q182429",
        "label": "metre per nanosecond",
        "siLabel": "metre per second"
    },
    "Q104628876": {
        "factor": "1000000",
        "unit": "Q182429",
        "label": "metre per microsecond",
        "siLabel": "metre per second"
    },
    "Q104628878": {
        "factor": "1000",
        "unit": "Q182429",
        "label": "metre per millisecond",
        "siLabel": "metre per second"
    },
    "Q104628879": {
        "factor": "100",
        "unit": "Q182429",
        "label": "metre per centisecond",
        "siLabel": "metre per second"
    },
    "Q104628880": {
        "factor": "10",
        "unit": "Q182429",
        "label": "metre per decisecond",
        "siLabel": "metre per second"
    },
    "Q104628881": {
        "factor": "0.1",
        "unit": "Q182429",
        "label": "metre per decasecond",
        "siLabel": "metre per second"
    },
    "Q104628882": {
        "factor": "0.01",
        "unit": "Q182429",
        "label": "metre per hectosecond",
        "siLabel": "metre per second"
    },
    "Q104628884": {
        "factor": "0.001",
        "unit": "Q182429",
        "label": "metre per kilosecond",
        "siLabel": "metre per second"
    },
    "Q104628885": {
        "factor": "0.000001",
        "unit": "Q182429",
        "label": "metre per megasecond",
        "siLabel": "metre per second"
    },
    "Q104628886": {
        "factor": "0.000000001",
        "unit": "Q182429",
        "label": "metre per gigasecond",
        "siLabel": "metre per second"
    },
    "Q104628887": {
        "factor": "0.000000000001",
        "unit": "Q182429",
        "label": "metre per terasecond",
        "siLabel": "metre per second"
    },
    "Q104628888": {
        "factor": "0.000000000000001",
        "unit": "Q182429",
        "label": "metre per petasecond",
        "siLabel": "metre per second"
    },
    "Q104628890": {
        "factor": "0.000000000000000001",
        "unit": "Q182429",
        "label": "metre per exasecond",
        "siLabel": "metre per second"
    },
    "Q104628891": {
        "factor": "0.000000000000000000001",
        "unit": "Q182429",
        "label": "metre per zettasecond",
        "siLabel": "metre per second"
    },
    "Q104628893": {
        "factor": "0.000000000000000000000001",
        "unit": "Q182429",
        "label": "metre per yottasecond",
        "siLabel": "metre per second"
    },
    "Q104629172": {
        "factor": "1000000000000000000000000000000000000000000000000",
        "unit": "Q1051665",
        "label": "metre per square yoctosecond",
        "siLabel": "metre per square second"
    },
    "Q104629174": {
        "factor": "1000000000000000000000000000000000000000000",
        "unit": "Q1051665",
        "label": "metre per square zeptosecond",
        "siLabel": "metre per square second"
    },
    "Q104629175": {
        "factor": "1000000000000000000000000000000000000",
        "unit": "Q1051665",
        "label": "metre per square attosecond",
        "siLabel": "metre per square second"
    },
    "Q104629176": {
        "factor": "1000000000000000000000000000000",
        "unit": "Q1051665",
        "label": "metre per square femtosecond",
        "siLabel": "metre per square second"
    },
    "Q104629177": {
        "factor": "1000000000000000000000000",
        "unit": "Q1051665",
        "label": "metre per square picosecond",
        "siLabel": "metre per square second"
    },
    "Q104629178": {
        "factor": "1000000000000000000",
        "unit": "Q1051665",
        "label": "metre per square nanosecond",
        "siLabel": "metre per square second"
    },
    "Q104629179": {
        "factor": "1000000000000",
        "unit": "Q1051665",
        "label": "metre per microsecond squared",
        "siLabel": "metre per square second"
    },
    "Q104629180": {
        "factor": "1000000",
        "unit": "Q1051665",
        "label": "metre per square millisecond",
        "siLabel": "metre per square second"
    },
    "Q104629181": {
        "factor": "10000",
        "unit": "Q1051665",
        "label": "metre per square centisecond",
        "siLabel": "metre per square second"
    },
    "Q104629182": {
        "factor": "100",
        "unit": "Q1051665",
        "label": "metre per square decisecond",
        "siLabel": "metre per square second"
    },
    "Q104629183": {
        "factor": "0.01",
        "unit": "Q1051665",
        "label": "metre per square decasecond",
        "siLabel": "metre per square second"
    },
    "Q104629184": {
        "factor": "0.0001",
        "unit": "Q1051665",
        "label": "metre per square hectosecond",
        "siLabel": "metre per square second"
    },
    "Q104629185": {
        "factor": "0.000001",
        "unit": "Q1051665",
        "label": "metre per square kilosecond",
        "siLabel": "metre per square second"
    },
    "Q104629186": {
        "factor": "0.000000000001",
        "unit": "Q1051665",
        "label": "metre per square megasecond",
        "siLabel": "metre per square second"
    },
    "Q104629187": {
        "factor": "0.000000000000000001",
        "unit": "Q1051665",
        "label": "metre per square gigasecond",
        "siLabel": "metre per square second"
    },
    "Q104629189": {
        "factor": "0.000000000000000000000001",
        "unit": "Q1051665",
        "label": "metre per square terasecond",
        "siLabel": "metre per square second"
    },
    "Q104629191": {
        "factor": "0.000000000000000000000000000001",
        "unit": "Q1051665",
        "label": "metre per square petasecond",
        "siLabel": "metre per square second"
    },
    "Q104629193": {
        "factor": "0.000000000000000000000000000000000001",
        "unit": "Q1051665",
        "label": "metre per square exasecond",
        "siLabel": "metre per square second"
    },
    "Q104629195": {
        "factor": "0.000000000000000000000000000000000000000001",
        "unit": "Q1051665",
        "label": "metre per square zettasecond",
        "siLabel": "metre per square second"
    },
    "Q104629197": {
        "factor": "0.000000000000000000000000000000000000000000000001",
        "unit": "Q1051665",
        "label": "metre per square yottasecond",
        "siLabel": "metre per square second"
    },
    "Q104786084": {
        "factor": "0.000000000001",
        "unit": "Q844211",
        "label": "picogram per litre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q104816242": {
        "factor": "0.0000000000235044",
        "unit": "Q177612",
        "label": "square arcsecond",
        "siLabel": "steradian"
    },
    "Q104816256": {
        "factor": "0.001",
        "unit": "Q844211",
        "label": "microgram per cubic centimetre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q104816263": {
        "factor": "1000",
        "unit": "Q844211",
        "label": "kilogram per cubic decimetre",
        "siLabel": "kilogram per cubic metre"
    },
    "Q104816550": {
        "factor": "0.0000000000000000001",
        "unit": "Q11573",
        "label": "nano\u00e5ngstr\u00f6m",
        "siLabel": "metre"
    },
    "Q104821935": {
        "factor": "0.000000000000000000153733",
        "unit": "Q1063756",
        "label": "microarcsecond per year",
        "siLabel": "radian per second"
    }
}
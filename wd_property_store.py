__author__ = 'Sebastian Burgstaller'
__licence__ = 'GPLv3'


domain_incompatibilities = {
    'drugs': [

    ],
    'genes': [

    ],
    'proteins': [

    ],
    'disease ontology': [

    ]
}

# a collection of values for the property 'instance of' (P31) which are valid for a certain domain.
valid_instances = {
    'drugs': [
        'Q11173',  # chemical compound (only one single, pure chemical compound)
        'Q79529',  # chemical substance (several defined chemical compounds)
        'Q8054',   # protein
        'Q12140',  # pharmaceutical drug
        'Q422248'  # monoclonal antibodies
    ],
    'genes': [

    ],
    'proteins': [

    ],
    'disease ontology': [

    ]
}

wd_properties = {
    'P715': {
        'datatype': 'string',
        'name': 'Drugbank ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P279': {
        'datatype': 'item',
        'name': 'subclass of',
        'domain': ['generic'],
        'core_id': 'False'
    },
    'P31': {
        'datatype': 'item',
        'name': 'instance of',
        'domain': ['generic'],
        'core_id': 'False'
    },
    'P636': {
        'datatype': 'item',
        'name': 'route of administration',
        'domain': ['drugs'],
        'core_id': 'False'
    },
    'P267': {
        'datatype': 'string',
        'name': 'ATC code',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P231': {
        'datatype': 'string',
        'name': 'CAS registry number',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P486': {
        'datatype': 'string',
        'name': 'MeSH ID',
        'domain': ['drugs', 'diseases'],
        'core_id': 'True'
    },
    'P672': {
        'datatype': 'string',
        'name': 'MeSH Code',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P662': {
        'datatype': 'string',
        'name': 'PubChem ID (CID)',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P661': {
        'datatype': 'string',
        'name': 'ChemSpider ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P652': {
        'datatype': 'string',
        'name': 'UNII',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P665': {
        'datatype': 'string',
        'name': 'KEGG ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P683': {
        'datatype': 'string',
        'name': 'ChEBI ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P274': {
        'datatype': 'string',
        'name': 'chemical formula',
        'domain': ['drugs'],
        'core_id': 'False'
    },
    'P592': {
        'datatype': 'string',
        'name': 'ChEMBL ID',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P233': {
        'datatype': 'string',
        'name': 'SMILES',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P234': {
        'datatype': 'string',
        'name': 'InChI',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P235': {
        'datatype': 'string',
        'name': 'InChIKey',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P1805': {
        'datatype': 'string',
        'name': 'Word Health Organisation International Nonproprietary Name',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P657': {
        'datatype': 'string',
        'name': 'RTECS Number',
        'domain': ['drugs'],
        'core_id': 'True'
    },
    'P699': {
        'datatype': 'string',
        'name': 'Disease Ontology ID',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P1550': {
        'datatype': 'string',
        'name': 'Orphanet ID',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P494': {
        'datatype': 'string',
        'name': 'ICD-10',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P493': {
        'datatype': 'string',
        'name': 'ICD-9',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P1395': {
        'datatype': 'string',
        'name': 'National Cancer Institute ID',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P1748': {
        'datatype': 'string',
        'name': 'NCI Thesaurus ID',
        'domain': ['diseases'],
        'core_id': 'True'
    },
    'P351': {
        'datatype': 'string',
        'name': 'Entrez Gene ID',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P703': {
        'datatype': 'item',
        'name': 'found in taxon',
        'domain': ['genes'],
        'core_id': 'False'
    },
    'P594': {
        'datatype': 'string',
        'name': 'Ensembl Gene ID',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P704': {
        'datatype': 'string',
        'name': 'Ensembl Transcript ID',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P353': {
        'datatype': 'string',
        'name': 'Gene symbol',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P354': {
        'datatype': 'string',
        'name': 'HGNC symbol',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P593': {
        'datatype': 'string',
        'name': 'homologene id',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P639': {
        'datatype': 'string',
        'name': 'RefSeq RNA ID',
        'domain': ['genes'],
        'core_id': 'True'
    },
    'P1057': {
        'datatype': 'item',
        'name': 'chromosome',
        'domain': ['genes'],
        'core_id': 'False'
    }
    # ,
    # '': {
    #     'datatype': 'string',
    #     'name': '',
    #     'domain': ['']
    # }
}
